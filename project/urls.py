from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'todo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^home/$', 'todo.views.home_page', name='home'),
    url(r'^admin/', include(admin.site.urls)),
)