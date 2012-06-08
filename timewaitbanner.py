#!/usr/bin/python


# Auto banner for lots of TIME_WAIT requests.
# requires ipset module installed.
# to work correct need to initialize ipset with:
#  $ ipset -N dropips iphash
# And add iptables rule:
#  $ iptables -A INPUT -m set --set dropips src -j DROP
# after it add execution of script into crontab

# Author Borovkov Ivan.
# email: v2nek.sev@gmail.com
# main script body was written 06/06/2012


import os
import re
import time
import datetime
import pickle

whitelist = ["127.0.0.1", "0.0.0.0", "78.47.190.166","95.132.82.81"]
banlogs = "/tmp/logban"
banhist = "/root/banhistory"

connections = os.popen("netstat -atun | grep TIME_WAIT | awk '{print $5}' | cut -d: -f1 | sed -e '/^$/d' |sort | uniq -c | sort -n").read()
conns=connections.split("\n")
conns.remove("")

normal = os.popen("netstat -atun | grep -v TIME_WAIT | awk '{print $5}' | cut -d: -f1 | sed -e '/^$/d' |sort | uniq -c | sort -n").read()
norm=normal.split("\n")
norm.remove("")


bannedipss = os.popen("ipset -L dropips").read()
bannedipss = bannedipss.split("\n")
bannedipss.remove("")

bannedips = []
for line in bannedipss:
    ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)
    if ( len(ip) > 0 ): bannedips.append(ip[0])

logs = open(banlogs, "a")
history = open(banhist, "a")

now = datetime.datetime.now()

for con in conns:
    con = con.split()
    #print con
    if ( int(con[0] ) > 150 ) and ( con[1] not in bannedips ) and ( con[1] not in whitelist ) and ( con[1] not in norm ):
#        banline = "iptables -A INPUT -s " + con[1] + "/32 -p tcp --dport 80 -j DROP"
        banline = "ipset -A dropips " + con[1]
        logs.write(str(int(time.time())) + " " +  con[1] + "\n")
        history.write(str(now.isoformat()) + " " +  con[1] + "\n")
        os.popen(banline)
#	print(banline)
logs.close()

#unbanning old entries

logs = open(banlogs, "r")
lines = logs.readlines()
#print(lines)
logs.close()

logs = open(banlogs, "w")
for line in lines:
    elem = line.strip()
#    print(elem)
    info = elem.split(" ")
#    print(info)
    diff = int(time.time()) - int(info[0])
#    print(diff)
    if ( diff > 12*60 ):
	unbanline = "ipset -D dropips " + info[1]
	lines.remove(line)
	os.popen(unbanline)
	#print(unbanline)
	#print("unbanned ip: " + info[1])

for line in lines:
    logs.write(line)

logs.close()