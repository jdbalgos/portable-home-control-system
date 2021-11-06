import requests
import json

def getDetails(ip):
    httpIP = 'http://' + ip
    req = requests.get(httpIP, timeout=1)
    newDict = req.json()
    return newDict

def getWifiCredentials(pointer):
    d = {}
    x = open('Config/config.ini','r')
    y = x.readlines()
    for line in y:
        z = line.split(",")
        a = z[0]
        b = z[1]
        d[a] = b
    return d[pointer]
    x.close()
