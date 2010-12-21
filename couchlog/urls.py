from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'couchlog.views.dashboard', name='couchlog_home'),
    url(r'^update/$', 'couchlog.views.update', name='couchlog_update'),
    url(r'^email/$', 'couchlog.views.email', name='couchlog_email'),
    url(r'^view/(?P<log_id>\w+)/$', 'couchlog.views.single', 
        {"display":"full"}, name='couchlog_single'),
    url(r'^searchdocs/$', 'couchlog.views.lucene_docs', name='lucene_docs'),
    
    url(r'^ajax/paging/$', 'couchlog.views.paging', name='couchlog_paging'),
    url(r'^ajax/single/(?P<log_id>\w+)/$', 'couchlog.views.single', 
        {"display":"ajax"}, name='couchlog_shortsingle'),
    
)
