from django.db import models

class FBUsers(models.Model):
    name            =   models.CharField(max_length=4000, null = True)
    user_id         =   models.CharField(max_length=100, null = True)
    page_id         =   models.CharField(max_length=100, null = True)
    written_in      =   models.IntegerField()
    
    def __unicode__(self):
        return self.name
    
class Page(models.Model):
#    name        =   models.TextField(null = True)
    user            =   models.ForeignKey(FBUsers, null = True)
    user_name       =   models.TextField()
    page_id         =   models.CharField(max_length=100, null = True)
    link            =   models.CharField(max_length=300, null = True)
    likes           =   models.IntegerField(default = 0)
    posts           =   models.IntegerField(default = 0)
    category        =   models.TextField(null = True)
    talking_about   =   models.IntegerField(default = 0)
    new_page        =   models.BooleanField(default = True)
    written_in      =   models.IntegerField()

    def __unicode__(self):
        return unicode(self.user_name)

class Post(models.Model):
    user            =   models.ForeignKey(FBUsers)
    page            =   models.ForeignKey(Page)
    post_id         =   models.CharField(max_length=100, null = True)
    created_date    =   models.DateField()
    link            =   models.CharField(max_length=100, null = True)
    msg             =   models.TextField()
    type            =   models.TextField(default = '')
    shares          =   models.IntegerField()
    likes           =   models.IntegerField()
    cmnts           =   models.IntegerField()
    written_in      =   models.IntegerField()
    
    def __unicode__(self):
        return unicode(self.post_id)

class Comment(models.Model):
    user            =   models.ForeignKey(FBUsers)
    post            =   models.ForeignKey(Post)
    cmnt_id         =   models.CharField(max_length=100, null = True)
    created_date    =   models.DateField()
    msg             =   models.TextField()
    likes           =   models.IntegerField()
    written_in      =   models.IntegerField()
    
    def __unicode__(self):
        return unicode(self.cmnt_id)

class Config(models.Model):
    access_token = models.CharField(max_length=200, null = True)
    
    def __unicode__(self):
        return self.access_token