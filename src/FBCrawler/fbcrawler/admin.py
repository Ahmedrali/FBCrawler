'''
Created on Jan 24, 2011

@author: aali
'''

from django.contrib import admin
from FBCrawler.fbcrawler.models import *
from django.http import HttpResponse
from django.core import serializers
from django.contrib.admin.views.main import ChangeList

class FBUsersAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'user_id'
                    )

class PageAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'user_name',
                    'page_id',
                    'link',
                    'likes',
                    'talking_about',
                    'posts',
                    'category',
                    'new_page'
                    )
    search_fields = ('user_name',)
    
class PostAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'page',
                    'post_id',
                    'created_date',
                    'link',
                    'msg',
                    'shares',
                    'likes',
                    'cmnts'
                    )
        
class CommentAdmin(admin.ModelAdmin):
    list_display = (
                    'user',
                    'post',
                    'cmnt_id',
                    'created_date',
                    'msg',
                    'likes'
                    )
    
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('access_token',
                    )

admin.site.register(FBUsers, FBUsersAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Config, ConfigAdmin)

def export_as_json(modeladmin, request, queryset):
    response = HttpResponse(mimetype="text/javascript")
    serializers.serialize("json", queryset, stream=response)
    response.__setitem__("Content-type", "application/octet-stream")
    response.__setitem__('Content-Disposition', 'attachment; filename="data.json"')
#    writeTofile("json.txt", response._get_content())
    return response

def export_as_xml(modeladmin, request, queryset):
    response = HttpResponse(mimetype="text/javascript")
    serializers.serialize("xml", queryset, stream=response)
    response.__setitem__("Content-type", "application/octet-stream")
    response.__setitem__('Content-Disposition', 'attachment; filename="data.xml"')
#    writeTofile("xml.txt", response._get_content())
    return response

def writeTofile(fileName, content):
        fout = open("export/%s" %fileName, "w")
        fout.write(content)
        fout.close()

admin.site.add_action(export_as_json, 'export_selected_as_json')
admin.site.add_action(export_as_xml, 'export_selected_as_xml')

