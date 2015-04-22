import urllib.request
import re
import time
import random
import socket

socket.setdefaulttimeout(3)

PAGES = 20

def saveProxy(proxy):
    f = open("proxies.txt", "a")
    f.write(proxy+"\n")
    f.close()

def testProxy(proxy):
    try:
        urllib.request.URLopener(
            {'http': 'http://'+proxy+"/"}).open("http://www.google.com")
    except IOError:
        try:
            urllib.request.URLopener(
                 {'https': 'https://'+proxy+"/"}).open("http://www.google.com")
        except IOError:
            print("Connection error! (Check proxy)")
            return None
        else:
            print("All was fine (HTTPS) ")
    else:
        print("All was fine (HTTP)")
    return proxy

def getProxies(page):
    # http://nntime.com/proxy-updated-01.htm
    page = str(page).zfill(2)
    url = "http://nntime.com/proxy-updated-{:}.htm".format(page)
    print("Getting:", url)
    queryToken = urllib.request.urlopen(url)

    response = queryToken.read().decode("latin-1")

    parseCode = r"((?:[a-z]=[0-9];)+)"
    matchesCode = re.findall(parseCode, response)
    print("Code", matchesCode)
    codes = {}
    for code in matchesCode[0].split(";")[:-1]:
        v = code.split("=")
        codes[v[0]] = v[1]

    print(codes)

    parseTable = r"<td>(.*?)</td>"
    matchesRow = re.findall(parseTable, response)
    # print(matchesRow)

    for row in matchesRow:
        m = re.findall(r'((?:[0-9]{1,3}\.){3}[0-9]{1,3})', row)
        if len(m) == 0:
            continue
        ip = m[0]

        pEnc = re.findall(r'document\.write\(":"((?:\+[a-z]){0,4})', row)
        portTmp = []
        if len(pEnc) > 0:
            pDec = pEnc[0].split("+")[1:]
            for c in pDec:
                portTmp.append(codes[c])
        else:
            continue
        port = "".join(portTmp)

        proxy = ip+":"+port

        print("Testing", proxy)
        p = testProxy(proxy)
        if p:
            saveProxy(p)

for page in range(1, PAGES):
    getProxies(page)
