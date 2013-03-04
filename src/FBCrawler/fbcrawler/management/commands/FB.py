import urllib2
import anyjson as json

class FB:
    
    def __init__(self):
        self.reqCounter = 0

    def getUserInfo(self, page):
        url = "https://graph.facebook.com/%s" %page.user_name
        resp = self.getResponse(url)
        parsed_resp = json.deserialize(resp)
        print parsed_resp
        return [
                parsed_resp['name'],
                parsed_resp.get('username',parsed_resp['id']),
                parsed_resp['id'],
                parsed_resp['link'],
                parsed_resp['likes'],
                parsed_resp['category'],
                parsed_resp['talking_about_count'],
                parsed_resp.get('talking_about_count',''),
                ]  
    
    def getData(self, url):
        resp = self.getResponse(url)
        parsed_resp = json.deserialize(resp)
        return parsed_resp
    
    def getResponse(self, url):
        resp = {}
        while True:
            try:
                self.reqCounter = self.reqCounter + 1
                print 'Req %s: %s' %(self.reqCounter, url)
                conn = urllib2.urlopen(url)
                resp = conn.read()
                conn.close()
                break
            except Exception, e:
                resp= {"error": "%s" %e}
                print e
                if resp['error'] == "HTTP Error 400: Bad Request":
                    return '{"error": "%s"}' %e
        return resp


