import os.path
import json
import urllib2
import urllib
import urlparse
import BaseHTTPServer
import webbrowser
import sys

APP_ID = '483547431694693'
APP_SECRET = 'd7ffcbdc6cb3dc9a2529ecedcb414ef5'
ENDPOINT = 'graph.facebook.com'
REDIRECT_URI = 'http://127.0.0.1:8080/'
ACCESS_TOKEN = None
LOCAL_FILE = 'fb_access_token'
STATUS_TEMPLATE = u"{name}\033[0m: {message}"

def get_url(path, args=None):
    args = args or {}
    if ACCESS_TOKEN:
        args['access_token'] = ACCESS_TOKEN
    if 'access_token' in args or 'client_secret' in args:
        endpoint = "https://"+ENDPOINT
    else:
        endpoint = "http://"+ENDPOINT
    return endpoint+path+'?'+urllib.urlencode(args)

def get(path, args=None):
    return urllib2.urlopen(get_url(path, args=args)).read()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
     
    def do_GET(self):
        global ACCESS_TOKEN
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
 
        code = urlparse.parse_qs(urlparse.urlparse(self.path).query).get('code')
        code = code[0] if code else None
        if code is None:
            self.wfile.write("Sorry, authentication failed.")
        response = get('/oauth/access_token', {'client_id':APP_ID,
                                               'redirect_uri':REDIRECT_URI,
                                               'client_secret':APP_SECRET,
                                               'code':code})
        ACCESS_TOKEN = urlparse.parse_qs(response)['access_token'][0]
        print 'ACCESS_TOKEN = ', ACCESS_TOKEN 
        open(LOCAL_FILE,'w').write(ACCESS_TOKEN)
        self.wfile.write("""
                            <html><body><center><h3>
                            You have successfully logged in to facebook.<br /> 
                            You can close this window now.
                            </h3></center></body></html>
                         """)
        
     
def print_status(item, color=u'\033[1;35m'):
    print color+STATUS_TEMPLATE.format(name=item['from']['name'],
                                       message=item['message'].strip())
     
if __name__ == '__main__':
    print "Logging you in to facebook..."
    webbrowser.open(get_url('/oauth/authorize',
                            {'client_id':APP_ID,
                             'redirect_uri':REDIRECT_URI,
                             'scope':'read_stream'}))
#    url = "http://www.facebook.com/dialog/oauth?response_type=token&display=popup&client_id=327836613926754&redirect_uri=http://127.0.0.1:8000/fb"
    httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8080), RequestHandler)
    while ACCESS_TOKEN is None:
        httpd.handle_request()
