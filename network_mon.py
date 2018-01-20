import subprocess
import re
import http.client
import urllib


def summary():
    for i in range(len(macs)):
        print(ips[i], macs[i], names[i])


def get_whitelisted():
    with open('whitelist.txt') as f:
        whitelisted = f.readlines()
        whitelisted = [x[0:17] for x in whitelisted]
        return whitelisted


def notify(ip, mac, name):
    print(ip, mac, name)

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
                 urllib.parse.urlencode({
                     "token": "app_token",
                     "user": "user_token",
                     "message": "Name: %s, IP: %s, MAC: %s" % (name, ip, mac),
                 }), {"Content-type": "application/x-www-form-urlencoded"})
    conn.getresponse()


nmap = subprocess.Popen(['nmap', '-sn', '192.168.0.0/24'],
                        stdout=subprocess.PIPE)
ipout = nmap.communicate()[0]

ips = []
macs = []
names = []

lines = ipout.splitlines()
for line in lines[2:-1]:
    line = str(line)
    if 'Nmap scan' in line:
        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)
        ips = ips + ip
    if 'MAC Address' in line:
        mac = re.findall(r'(?:[0-9a-fA-F]:?){12}', line)
        macs = macs + mac
        name = line[line.find("(")+1:line.find(")")]
        names.append(name)

summary()
not_whitelisted = set(macs) - set(get_whitelisted())
if len(not_whitelisted) > 0:
    for item in not_whitelisted:
        index = macs.index(item)
        notify(ips[index], macs[index], names[index])
