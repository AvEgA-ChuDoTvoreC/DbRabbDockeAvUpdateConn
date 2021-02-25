#FROM ubuntu:20.04
#FROM ubuntu:16.04
FROM ubuntu:bionic

VOLUME /usr/src/app/logs/ /usr/src/app/webconf/

## Install Python
RUN apt-get update -y && apt-get install -y software-properties-common && apt-get update -y \
    && apt-get install -y python3 \
    python3-pip \
    locales

## Install Test Tools (ps - procps; ip a - iproute2; ping - iputils-ping; ...
RUN apt-get install -y \
    iproute2 \
    procps \
    vim \
    net-tools \
    ssh \
    iputils-ping \
    tcpdump \
    bridge-utils

## Set Up Timezone Settings and Install Requirements
# (pika==0.13.1 requests psutil py-postgresql ...)
COPY requirements.txt /usr/src/app/
RUN pip3 install -r /usr/src/app/requirements.txt \
    && ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo Europe/Moscow > /etc/timezone \
    && locale-gen en_US.UTF-8

RUN apt-get install \
    tzdata \
    && dpkg-reconfigure -f noninteractive tzdata

# All environment variables also can be set in .env file (docker use .env file at building process)
# To list all env variablles type:        $ printenv
# To check virtualenv you're working at:  $ echo $VIRTUAL_ENV
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

COPY start.sh \
    script.sh \
    work_sql.py \
    main.py \
    /usr/src/app/

## Methods
#COPY file1.txt /files/

## Copy Test Python Tools
COPY pytools/port_scanner.py \
    pytools/port_scanner_default.py \
    pytools/pygamemusic.py \
    /usr/src/app/pytools/

COPY baseconfig/ /usr/src/app/baseconfig
COPY dbtemplates/ /usr/src/app/dbtemplates

WORKDIR /usr/src/app/

RUN chmod +x /usr/src/app/start.sh
RUN chmod +x /usr/src/app/script.sh

ENTRYPOINT ["bash", "script.sh"]

