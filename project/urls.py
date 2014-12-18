from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'project.views.login'),
    #todo app urls
    (r'^todo/', include('todo.urls')),
    #user authentication urls
    url(r'^accounts/login/$', 'project.views.login'),
    url(r'^accounts/auth/$', 'project.views.auth_view'),
    url(r'^accounts/logout/$', 'project.views.logout'),
    url(r'^accounts/invalid/$', 'project.views.invalid_login'),
    url(r'^accounts/unauthorized/$', 'project.views.unauthorized'),
    #url(r'^admin/', include(admin.site.urls)),
)
