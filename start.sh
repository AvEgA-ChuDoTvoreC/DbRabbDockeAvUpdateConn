#!/bin/bash
#
# start.sh
#


echo "STEP I. Creating docker network. Creating DNS server."


## Choose docker network name here:
net_create="MYNETWORK"


net_inspect=$(docker network ls | grep -w "${net_create}" | awk '{print $1}')
echo ${net_inspect}
if [[ -n "${net_inspect}" ]]; then
    echo "Docker network: ${net_create} already exist. Pass through this step."
else
    echo "Docker network: ${net_create} was not found. Creating..."
    docker network create --driver bridge --subnet 172.19.2.0/24 --ip-range 172.19.2.0/24 ${net_create}
fi
sleep 4
#docker rm -f dnss
#docker run -d --name=dnss --dns=127.0.0.1 \
#    --publish=172.18.1.8:53:53/udp \
#    --publish=172.18.1.8:10000:10000 \
#    --volume=/src/docker/dnss:/data \
#    --env="ROOT_PASSWORD=aa" \
#    sameersbn/bind:latest

# set variables
local_dns="172.19.1.8"
#--dns=${local_dns_rb} \
#--dns=${local_dns_db} \

## apt-get update && apt-get install -y iputils-ping
## cat /etc/resolv.conf
## apt install bridge-utils     ->

### https://stackoverflow.com/questions/20430371/my-docker-container-has-no-internet
#First thing to check is run cat /etc/resolv.conf in the docker container.
# If it has an invalid DNS server, such as nameserver 127.0.x.x, then the container will not be able to resolve
# the domain names into ip addresses, so ping google.com will fail.
#
#Second thing to check is run cat /etc/resolv.conf on the host machine. Docker basically copies
# the host's /etc/resolv.conf to the container everytime a container is started. So if the
# host's /etc/resolv.conf is wrong, then so will the docker container.
#
#If you have found that the host's /etc/resolv.conf is wrong, then you have 2 options:
#
#Hardcode the DNS server in daemon.json. This is easy, but not ideal if you expect the DNS server to change.
#Fix the hosts's /etc/resolv.conf. This is a little trickier, but it is generated
# dynamically, and you are not hardcoding the DNS server.
#1. Hardcode DNS server in docker daemon.json
#
#Edit /etc/docker/daemon.json
#
#{
#    "dns": ["10.1.2.3", "8.8.8.8"]
#}
#Restart the docker daemon for those changes to take effect:
#sudo systemctl restart docker
#Now when you run/start a container, docker will populate /etc/resolv.conf with the values from daemon.json.
#2. Fix the hosts's /etc/resolv.conf
#
#A. Ubuntu 16.04 and earlier
#
#For Ubuntu 16.04 and earlier, /etc/resolv.conf was dynamically generated by NetworkManager.
#Comment out the line dns=dnsmasq (with a #) in /etc/NetworkManager/NetworkManager.conf
#Restart the NetworkManager to regenerate /etc/resolv.conf :
#sudo systemctl restart network-manager
#Verify on the host: cat /etc/resolv.conf
#B. Ubuntu 18.04 and later
#
#Ubuntu 18.04 changed to use systemd-resolved to generate /etc/resolv.conf. Now by default it uses a local
# DNS cache 127.0.0.53. That will not work inside a container, so Docker will default to Google's 8.8.8.8 DNS server,
# which may break for people behind a firewall.
#/etc/resolv.conf is actually a symlink (ls -l /etc/resolv.conf) which
# points to /run/systemd/resolve/stub-resolv.conf (127.0.0.53) by default in Ubuntu 18.04.
#Just change the symlink to point to /run/systemd/resolve/resolv.conf, which lists the real DNS servers:
#sudo ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
#Verify on the host: cat /etc/resolv.conf
#Now you should have a valid /etc/resolv.conf on the host for docker to copy into the containers.


echo "STEP II. Creating RabbitMQ Server"

##
## By default  /etc/rabbitmq/rabbitmq.conf  holds next lines:
## loopback_users.guest = false
## listeners.tcp.default = 5672
## management.tcp.port = 15672
## Here you can change ports to work with
##
### 172.19.2.8  rabmq.deliver.ru  5668:5672
### 172.19.2.9  db.storage.ru     5669:3306

rbmq_login="deliver"
rbmq_pass="qwerttty"
rbmq_port="5668"
rbmq_container_port="5672"
rbmq_name="rbmq"
rbmq_hostname="rabmq.deliver.ru"
rbmq_ip="172.19.2.8"

#

# start RabbitMQ Server
docker rm -f ${rbmq_name}
docker run -d --network=${net_create} \
    --restart unless-stopped \
    --ip=${rbmq_ip} \
    --name=${rbmq_name} \
    --hostname=${rbmq_hostname} \
    -p 22600:15672 -p ${rbmq_port}:${rbmq_container_port} \
    --volume=/opt/challenge/rabbitmq/${rbmq_login}:/var/lib/rabbitmq \
    rabbitmq:3-management
sleep 10
docker exec ${rbmq_name} /bin/bash -c "rabbitmqctl wait /var/run/rabbitmq/pid; rabbitmqctl add_user ${rbmq_login} ${rbmq_pass};rabbitmqctl set_permissions -p / ${rbmq_login} '.*' '.*' '.*';rabbitmqctl set_user_tags ${rbmq_login} administrator;rabbitmq-plugins enable rabbitmq_management"


echo "STEP III. Creating MySQL Server"


db_login="admin"
db_pass="qwerty"
db_port="5669"
db_container_port="3306"
db_name="sql2"
db_hostname="db.storage.ru"
db_docker_machine_ip="172.19.2.9"

# start DataBaseSQL Server
docker rm -f ${db_name}
docker run -d --network=${net_create} \
    --restart unless-stopped \
    --ip=${db_docker_machine_ip} \
    --name=${db_name} \
    --hostname=${db_hostname} \
    -p 22800:33060 -p ${db_port}:${db_container_port} \
    -e MYSQL_ROOT_PASSWORD=${db_pass} \
    -e MYSQL_ROOT_HOST=${db_docker_machine_ip} \
    -e MYSQL_USER=${db_login} \
    -e MYSQL_PASSWORD=${db_pass} \
    -e MYSQL_DATABASE=DataBaseSQL \
    --volume=/opt/challenge/database/data/:/var/lib/mysql/ \
    --volume=/opt/challenge/database/mysql/:/docker-entrypoint-initdb.d/ \
    mysql:5.7
#    sh -c "exec mysql -u${db_login} -p${db_pass} --protocol=tcp -h${db_docker_machine_ip} -P${db_port}"
#    --volume=/opt/challenge/postgresql/webconf/mysql.cnf:/etc/mysql/conf.d/mysql.cnf \
#    --volume=/opt/challenge/postgresql/db/conf/:/etc/mysql/ \
#    sed 's|.*bind-address *.= *[0-9\.]*|bind-address    = 172.19.2.8|g' /etc/mysql/mysql.conf.d/mysqld.cnf
#    /etc/init.d/mysql restart
#    https://phoenixnap.com/kb/mysql-remote-connection
#    https://linuxize.com/post/mysql-remote-access/
#    https://serverfault.com/questions/352503/how-do-i-allow-remote-mysql-access-to-a-single-static-ip
#
echo "STEP IV. Creating Main container with program"


# -conf
dir_wconf="/opt/challenge/postgresql/webconf"
container_dir_wconf="/usr/src/app/webconf"
# -logs
dir_logs="/opt/challenge/postgresql/logs"
container_dir_logs="/logs"
# -input_files
dir_files="/opt/challenge/postgresql/files"
container_dir_files="/files"
# -output_files
dir_files_output="/opt/challenge/postgresql/extra"
container_dir_files_output="/extra"

# Names
container_image="main_image"
container_name="main_db"
dockerfile_name="Dockerfile"
container_ip="172.19.2.2"


# Building process
docker rm -f ${container_name}
echo "Start building main container"
docker build -t ${container_image} -f ${dockerfile_name} .
echo "Sleep before run..."
sleep 15
docker run -it --rm --network=${net_create} \
    --name=${container_name} \
    --ip=${container_ip} \
    -p 15631:15631 \
    --link ${db_name}:mysql \
    -v ${dir_wconf}:${container_dir_wconf} \
    -v ${dir_logs}:${container_dir_logs} \
    -v ${dir_files}:${container_dir_files} \
    -v ${dir_files_output}:${container_dir_files_output} \
    ${container_image}

sleep 1
echo "Finnish!"
