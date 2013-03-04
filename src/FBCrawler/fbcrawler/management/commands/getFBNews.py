from django.core.management.base import BaseCommand
from FBCrawler.fbcrawler.models import *
from FBCrawler.fbcrawler.management.commands.FB import FB
import datetime

class Command(BaseCommand):
    args = '<>'
    help = 'Get user details'
    access_token = ''
    h = FB()
    def requestAccessToken(self):
        key = Config.objects.all()
        while len(key) == 0:
            return False
        self.access_token = key[0].access_token
        return True
    
    def handle(self, *args, **options):
        found = self.requestAccessToken()
        if not found:
            return

        fb_pages = Page.objects.all()
        self.written_in_date = (int)("%s%s%s" %(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day))
        for page in fb_pages:
            if page.new_page:
                info = self.h.getUserInfo(page)
                self.savePageInfo(page, info)
            
            page_url = "https://graph.facebook.com/%s/posts?access_token=%s" %(page.page_id, self.access_token)
            while page_url != "":
                posts = self.h.getData(page_url)
                posts = self.checkError(page_url, posts)
                
                print "\n\n"
                print "** page_url = ", page_url
                
                if 'posts' in posts and 'paging' in posts['posts'] and 'next' in posts['posts']['paging']:
                    page_url = posts['posts']['paging']['next']
                elif 'paging' in posts and 'next' in posts['paging']:
                    page_url = posts['paging']['next']
                else:
                    page_url = ''
            
                try:
#                    posts_list = posts['posts']['data']
                    posts_list = posts['data']
                    
                    print "\n"
                    print "** Length of posts_list = ", len(posts_list)
                
                    post_num = 1
                    for post in posts_list:
                        post_num = self.printInc("Post Num", post_num)
                        print post['id']
                        [new_post, comment_count] = self.savePostInfo(page, post)
                        print "\n"
                        print "** Comments Count = ", comment_count
                        post_url = "https://graph.facebook.com/%s/comments?limit=100&access_token=%s" %(new_post.post_id, self.access_token)#&limit=900
                        while post_url != "":
                            comments = self.h.getData(post_url)
                            comments = self.checkError(post_url, comments)
                            
                            if 'comments' in comments and 'paging' in comments['comments'] and 'next' in comments['comments']['paging']: 
                                post_url = comments['comments']['paging']['next']
                            elif 'paging' in comments and 'next' in comments['paging']:
                                post_url = comments['paging']['next']
                            else:
                                post_url = ''
                                
                            print "\n\n"
                            print "** post_url = ", post_url
                            
                            try:
#                                comments_list = comments['comments']['data']
                                comments_list = comments['data']
                                cmnt_num = 1
                                for comment in comments_list:
                                    cmnt_num = self.printInc("Comment Num", cmnt_num)
                                    self.saveCommentInfo(new_post, comment)
                            except:
                                pass
                except:
                    pass
                
            page.posts = Post.objects.filter(page = page).count()
            page.save()
    
    def saveFBUserInfo(self, name, id):
        if len(FBUsers.objects.filter(name = name)) == 0:
            fb_user = FBUsers()
            fb_user.name       =   name
            fb_user.user_id    =   id
            fb_user.written_in =   self.written_in_date
            fb_user.save()
        else:
            fb_user = FBUsers.objects.get(name = name)
            
        return fb_user
    
    def savePageInfo(self, page, info):
        name    = info[0]
        id      = info[2]
        
        fb_user =   self.saveFBUserInfo(name, id)   
        
        page.user           =   fb_user
        page.page_id        =   id
        page.link           =   info[3]
        page.likes          =   info[4]
        page.category       =   info[5]
        page.talking_about  =   info[6]
        page.new_page       =   False
        page.written_in     =   self.written_in_date
        page.save()
    
    def savePostInfo(self, page, post):
        post_id = post['id']
        if Post.objects.filter(post_id = post_id).count() == 0:
            from_name   =   post["from"]["name"]
            from_id     =   post["from"]["id"]
            fb_user =   self.saveFBUserInfo(from_name, from_id)
                
            new_post = Post()
            new_post.user           =   fb_user
            new_post.page           =   page
            new_post.post_id        =   post_id   
            new_post.created_date   =   self.getDate(post['created_time'])   
            new_post.link           =   post.get('link','')
            new_post.msg            =   self.getMessage(post)
            new_post.type           =   post.get('type','')
            try:
                shares  =   post['shares']['count']
            except:
                shares  =   0
            try:
                likes  =   post['likes']['count']
            except:
                likes  =   0
            try:
                comments  =   post['comments']['count']
            except:
                comments  =   0
            new_post.shares         =   shares
            new_post.likes          =   likes
            new_post.cmnts          =   comments
            new_post.written_in     =   self.written_in_date
            new_post.save()
        else:
            new_post = Post.objects.get(post_id = post_id)
        return [new_post, new_post.cmnts]
    
    def saveCommentInfo(self, post, comment):
        cmnt_id  = comment['id']
        if Comment.objects.filter(cmnt_id = cmnt_id).count() == 0:
            from_name   =   comment["from"]["name"]
            from_id     =   comment["from"]["id"]
            fb_user     =   self.saveFBUserInfo(from_name, from_id)
            
            new_comment                 =   Comment()
            new_comment.user            =   fb_user
            new_comment.post            =   post
            new_comment.cmnt_id         =   cmnt_id
            new_comment.created_date    =   self.getDate(comment['created_time'])
            new_comment.msg             =   comment['message']
            new_comment.likes           =   comment['like_count']
            new_comment.written_in      =   self.written_in_date
            new_comment.save()
    
    def getDate(self, date):
        d = date.split('-')
        date = datetime.date(int(d[0]), int(d[1]), int(d[2][0:2]))
        return date
    
    def getMessage(self, post):
        if 'message' in post:
            message = post['message']
        else:
            if 'story' in post:
                message = post['story']
            else:
                message = post['name']
        message = message.replace("<p>", " ")
        message = message.replace("</p>", " ")
        message = message.replace("&nbsp;", " ")
        message = message.replace("<br />", "\n")
        message = message.replace("<br>", "\n")
        return message
    
    def checkError(self, url, res):
        if 'error' in res:
            print "*-* Request An AccessToken *-*"
            self.requestAccessToken()
            acc = url[url.find("access_token=")+13 : url.find('&')]
            url = url.replace(acc, self.access_token)
            return self.h.getData(url)
        else:
            return res
    
    def printInc(self, msg, i):
        print "%s : %s" %(msg, i)
        i += 1
        return i
    
    def updateUserPages(self):
        users = FBUsers.objects.all()
        for user in users:
            print user.user_id
            comment = Comment.objects.filter(user = user)[0]
#            post = Post.objects.filter(id = comment.post)
            page_id = comment.post.page.page_id
            print "User = %s, Page = %s" %(user.user_id, page_id)
            user.page_id = page_id
            user.save()