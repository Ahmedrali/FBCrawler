from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from FBCrawler.fbcrawler.models import Page, Post, Comment, Config
import csv
from django.template import loader, Context
import urllib
import urllib2
import urlparse
from management.commands import anyjson as json
import datetime

APP_ID = '483547431694693'
APP_SECRET = 'd7ffcbdc6cb3dc9a2529ecedcb414ef5'
ENDPOINT = 'graph.facebook.com'
REDIRECT_URI = 'http://127.0.0.1:8000/accTokHandling'

def index(request):
    message = getRemainingTimeMessage()
    return render_to_response('index.html', Context({"message": message}))

def addNewPage(request):
    pages = request.POST.get('new_pages')
    pages = pages.split(',')
    num_exist = 0
    num_added = 0
    not_exist_in_fb = []
    for page in pages:
        sPage = page.strip()
        if len(sPage) > 0: 
            empty = sPage.__len__() == 0
            exist = Page.objects.filter(user_name = sPage).__len__() > 0
            existInFB = checkExistence(sPage)
            if (not empty) and (not exist) and existInFB:
                new_page = Page()
                new_page.user_name = sPage
                new_page.written_in= 0
                new_page.save()
                num_added += 1
            else:
                if exist:
                    num_exist += 1
                if not existInFB:
                    not_exist_in_fb.append(page)
    res_text = ""
    if num_added > 0:
        res_text = "Congratulations... Your %s page(s) are added successfully.<br />" %(num_added)
    if num_exist > 0:
        res_text +=  "%s page(s) are already exist.<br />" %( num_exist)
    if len(not_exist_in_fb) > 0:
        res_text += "Check again the following page(s):<br />"
        for page in not_exist_in_fb:
            res_text += "- %s<br />" %page
    return HttpResponse(res_text)

def getFBLinks(request):
    outFile = open('srclinks.csv', 'w')
    links = request.POST.get('new_pages')
    links = links.split(',')
    for link in links:
        line = "%s\n" %link
        outFile.write(line)
    outFile.colse()
    return HttpResponse("Extracting Facebook Links...")

def renewAccessToken(request):
    url = get_url('/oauth/authorize',
                                    {'client_id':APP_ID,
                                     'redirect_uri':REDIRECT_URI,
                                     'scope':'read_stream'})
    return redirect(url)

def accTokHandling(request):    
    code = urlparse.parse_qs(urlparse.urlparse(request.get_full_path()).query).get('code')
    code = code[0] if code else None
    if code is None:
        return render_to_response('index.html', Context({"message": 'Sorry, authentication failed, Please feel free to mail "ahmedrali2@gmail.com" for support, Thanks.'}))

    short_access_token = getShortAccessToken(code)
    long_access_token = getLongAccessToken(short_access_token)
    
    Config.objects.all().delete()
    Config(access_token = long_access_token).save()
    return render_to_response('index.html', Context({"message": "Congratulations, Your new session is created successfully."}))

def csv(request):
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=data.csv'

    # The data is hard-coded here, but you could load it from a database or
    # some other source.
    csv_data = []
    pages = Page.objects.all()
    for page in pages:
        posts = Post.objects.filter(page = page)
        for post in posts:
            comments = Comment.objects.filter(post = post)
            for comment in comments:
                csv_data.append([page.user_name.encode("utf8"), post.msg.encode("utf8"), post.created_date, comment.msg.encode("utf8"), comment.created_date])

    t = loader.get_template('template.txt')
    c = Context({
        'data': csv_data,
    })
    response.write(t.render(c))
    return response

##
# utility functions
##

def checkExistence(page):
    if page != "":
        try:
            url  = "https://graph.facebook.com/%s" %page
            conn = urllib2.urlopen(url)
            resp = conn.read()
            conn.close()
            resp = json.deserialize(resp)
            user_id   = resp.get("id","")
            if len(user_id) >= 12:
                return True
            return False
        except Exception:
            return False
    return False

def getRemainingTimeMessage():
    acc_tok = Config.objects.all()
    message = ""
    if len(acc_tok) > 0:
        try:
            acc_tok = acc_tok[0].access_token
            resp = get("/debug_token", {'input_token': acc_tok, 'access_token':acc_tok})
            resp = json.deserialize(resp)
            if "error" not in resp and "data" in resp and "expires_at" in resp["data"]:
                expires_at = (int)(resp["data"]["expires_at"])
                expires_date = datetime.datetime.fromtimestamp(expires_at)
                remaining_days = (expires_date - datetime.datetime.now()).days
                if remaining_days > 0:
                    message = "You have %s day(s) in your current Facebook session." %(remaining_days)
                else:
                    message = 'You need to renew you Facebook session. Please click on "Renew Facebook Session" below...'
        except:
            pass
    return message

def getShortAccessToken(code):
    
    response = get('/oauth/access_token', {'client_id':APP_ID,
                                           'redirect_uri':REDIRECT_URI,
                                           'client_secret':APP_SECRET,
                                           'code':code})
    access_token = urlparse.parse_qs(response)['access_token'][0]
    print "short: %s" %access_token
    return access_token

def getLongAccessToken(access_token):
    params = urllib.urlencode({ 
                               'client_id':'483547431694693', 
                                'client_secret':'d7ffcbdc6cb3dc9a2529ecedcb414ef5',
                                'grant_type':'fb_exchange_token',
                                'fb_exchange_token':access_token # Short Access Token to get the long one
                                })
    url = 'https://graph.facebook.com/oauth/access_token?' + params
    conn = urllib.urlopen(url)
    res  = conn.read()
    access_token = urlparse.parse_qs(res)['access_token'][0]
    print "long: %s" %access_token
    return access_token

def get_url(path, args=None):
    args = args or {}
    if 'access_token' in args or 'client_secret' in args:
        endpoint = "https://"+ENDPOINT
    else:
        endpoint = "http://"+ENDPOINT
    return endpoint+path+'?'+urllib.urlencode(args)

def get(path, args=None):
    return urllib2.urlopen(get_url(path, args=args)).read()    