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
        # url(r'^news/$', views.newsPage, name='newsPage'),
        # url(r'^agenda/$', views.agenda, name='agenda'),
        url(r'^changelog/$', views.changelog, name='changelog'),
        url(r'^adminlogin/$', views.loginPage, name='adminlogin'),
        url(r'^admin/$', views.adminPanel, name='admin'),
        url(r'^admin/clearcache/$', views.adminClearCache, name='adminClearCache'),
        url(r'^admin/changepass/$', views.adminChangePassword, name='adminChangePassword'),
        url(r'^admin/modifyaliases/$', views.adminModifyAliases, name='adminModifyAliases'),
        url(r'^admin/logout/$', views.adminLogout, name='adminLogout'),
        url(r'^admin/updatecache/$', views.adminUpdateCache, name='adminUpdateCache'),
        url(r'^admin/modifypriority/$', views.adminModifyPriority, name='adminModifyPriority'),
        url(r'^admin/adminupdateID/$', views.adminUpdateID, name='adminUpdateID')
]
