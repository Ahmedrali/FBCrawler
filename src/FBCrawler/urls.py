from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('fbcrawler.views',
    (r'^$', 'index'),
    (r'^/$', 'index'),
    (r'^addNewPage$', 'addNewPage'),
    (r'^csv$', 'csv'),
    (r'^renewAccessToken$', 'renewAccessToken'),
    (r'^accTokHandling$', 'accTokHandling'),
    # Examples:
    # url(r'^$', 'FBCrawler.views.home', name='home'),
    # url(r'^FBCrawler/', include('FBCrawler.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)
