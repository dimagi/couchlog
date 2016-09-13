from django.conf.urls import patterns, url

from couchlog.views import (
    dashboard,
    email,
    lucene_docs,
    paging,
    single,
    update,
)

urlpatterns = patterns('',
    url(r'^$', dashboard, name='couchlog_home'),
    url(r'^update/$', update, name='couchlog_update'),
    url(r'^email/$', email, name='couchlog_email'),
    url(r'^view/(?P<log_id>\w+)/$', single,
        {"display":"full"}, name='couchlog_single'),
    url(r'^searchdocs/$', lucene_docs, name='lucene_docs'),
    
    url(r'^ajax/paging/$', paging, name='couchlog_paging'),
    url(r'^ajax/single/(?P<log_id>\w+)/$', single,
        {"display":"ajax"}, name='couchlog_shortsingle'),
    
)
