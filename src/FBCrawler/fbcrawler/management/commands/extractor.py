import re
import urllib2
import anyjson as json

from django.core.management.base import BaseCommand
import socket

class Command(BaseCommand):
    
    def __init__(self):
        self.fbLinksFile    = ""
        self.urls           = []
        
    def readLinks(self):
        src = open('sample_srclinks.csv', 'r')
        self.urls = src.readlines()
        self.urls = list(set(self.urls))
        self.urls.sort()
        print "%s Found..." %(len(self.urls))
        src.close()
        
    def handle(self, *args, **options):
        self.readLinks()
        i = 1
        lines = []
        for url in self.urls:
            res = self.getFBLinks(i, url)
            if res == "": # Search for redirect URL
                new_url = self.hasJS(url)
                if new_url != "":
                    res = self.getFBLinks(i, new_url)
                if new_url == "" or res == "":
                    if self.hasFlash(url):
                        res = '"%s","[[Flash]]"'%url.strip()
            lines.append(res)
            print res
            i += 1
        self.writeResult(lines)

    def writeResult(self, res):
        self.fbLinksFile = open('fblinks.csv', 'w')
        for r in res:
            if r != "":
                try:
                    self.fbLinksFile.write(r)
                except:
                    tmp = r.split(",")
                    self.fbLinksFile.write('"%s","%s"'%(tmp[0], tmp[1]))
                self.fbLinksFile.write("\n")
        self.fbLinksFile.close()
    
    def getFBLinks(self, i, url):
        lines = ""
        url = url.strip()
        print "%s reading: %s" %(i, url)
        data = self.getData(url)
        accounts = self.hasFB(data)
        for account in accounts:
            tmp = account.split(",")
            line = '"%s","%s","%s"'%(url,tmp[0], tmp[1])
            lines += line
        return lines
    
    def getData(self, url):
        try:
            if not url.startswith("http://"):
                url = "http://%s" %url
            conn = urllib2.urlopen(url, timeout = 10)
            res  = conn.read()
        except Exception as e:
            res  = "ERR: %s" %e
        except socket.timeout as e:
            print "TimeOut..."
        return res
    
    def hasFlash(self, url):
        url = url.strip()
        data = self.getData(url)
        if data.find(".swf") != -1:
            return True
        return False
    
    def hasJS(self, url):
        url = url.strip()
        data = self.getData(url)
        pattern = 'document.location.href="\/[^"]*'
        p = re.compile(pattern)
        page = p.findall(data)
        if len(page) == 1:
            page = page [0]
            new_url = url + page[page.find("/"):len(page)]
            return new_url
        return ""
    
    def hasFB(self, data):
        links = []
        patterns = ["www.facebook.com[^\s\"<>]*"]
        for pattern in patterns: 
            p = re.compile(pattern)
            links.extend(p.findall(data))
        links = self.filterFBlinks(list(set(links)))
        return links
    
    def filterFBlinks(self, fbs):
        res = []
        patterns = ["\/[A-Za-z0-9\.]*", "\d{15}", "\d{12}"]
        ids = []
        for fb in fbs:
            for pattern in patterns: 
                p = re.compile(pattern)
                ids.extend(p.findall(fb))
        ids = set(ids)
        for id in ids:
            if (id.isdigit() and len(id) == 15) or (id.isdigit() and len(id) == 12) or (id != "/" and id.find(".php") == -1 and not id.isdigit()):
                r = self.Exist(id)
                if r != "":
                    res.append(r)
        res = set(res)                      
        return res
    
    def Exist(self, id):
        if id != "":
            try:
                url  = "https://graph.facebook.com/%s" %id
                conn = urllib2.urlopen(url)
                resp = conn.read()
                conn.close()
                resp = json.deserialize(resp)
                user_name = resp.get("name", "")
                user_id   = resp.get("id","")
                if len(user_id) >= 12:
                    return "%s,%s" %(user_id, user_name)
                return ""
            except Exception:
                return ""