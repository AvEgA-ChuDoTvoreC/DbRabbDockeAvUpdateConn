import os
import json
import requests
import pymysql


f = """en
conf t
no int Gi0/0/0.300
no int Gi0/0/0.301
no int Gi0/0/0.302
int range gi0/0/0-2
 channel-group 1 mode active
interface Port-channel1.300
 encapsulation dot1Q 300
 vrf forwarding Management
 ip address 10.16.19.35 255.255.255.248"""

l = []
for i, command in enumerate(f.split("\n"), 1):
    print('action {:04} cli command "{}"'.format(i, command.rstrip()))
    l.append('action {:04} cli command "{}"'.format(i, command.rstrip()))

print(list(filter(lambda x: x.split()[-1].strip('"') in f, l)))
print(dir())
print(os.getlogin())
print(os.getcwd())

fmt = " :[{:<20}]: "
print(fmt.format('%(filename)s.%(lineno)d'))
