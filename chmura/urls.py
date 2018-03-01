from django.conf.urls import url
from . import views
from . import api

urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^index.html$', views.index, name='index'),
        url(r'^timetable/$', views.index, name='index'),
        url(r'^announcement/$', views.announcement, name='announcement'),
        url(r'^substitution/$', views.substitutionList, name='substitutionList'),
        url(r'^webapi/$', api.webapi, name='webapi'),
        url(r'^news/$', views.newsPage, name='newsPage'),
        url(r'^agenda/$', views.agenda, name='agenda'),
        url(r'^changelog/$', views.changelog, name='changelog'),
        url(r'^login/$', views.loginPage, name='loginPage'),
        url(r'^adminPanel/$', views.adminPanel, name='adminPanel'),
        url(r'^adminPanel/clearCache/$', views.adminClearCache, name='adminClearCache'),
        url(r'^adminPanel/changePass/$', views.adminChangePassword, name='adminChangePassword'),
        url(r'^adminPanel/modifyAliases/$', views.adminModifyAliases, name='adminModifyAliases'),
]
