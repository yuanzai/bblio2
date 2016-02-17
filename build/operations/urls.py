from django.conf.urls import url
import operations.views
import operations.views.admin
import operations.views.site

urlpatterns = [
    url(r'^$', operations.views.index, name='index'),
    
    # admin

    url(r'^admin/$', operations.views.admin.index, name='admin'),
    url(r'^admin/push_scrape/$', operations.views.admin.push_scrape, name='admin_push'),

    # phrases
    url(r'^phrases/$', operations.views.phrases, name='phrases'),
    

    # site
    url(r'^site/$',
        operations.views.site.sites, name='sites'),
    url(r'^site/(?P<site_id>\d+)/$',
        operations.views.site.site,name='site'),
    
    # 1 - tree
    url(r'^tree/$', operations.views.site.tree,name='tree'),

    # 2 - input
    url(r'^site/(?P<site_id>\d+)/delete/$',
        operations.views.site.delete, name='delete'),
    
    # 3 - crawling
    url(r'^site/(?P<site_id>\d+)/crawl/$',
        operations.views.site.crawl, name='crawl'),
    
    url(r'^site/(?P<site_id>\d+)/crawl_cancel/$',
        operations.views.site.crawl_cancel, name='crawl_cancel'),
    
    url(r'^site/(?P<site_id>\d+)/crawl_not_running/$',    
        operations.views.site.crawl_not_running, name='crawl_not_running'),
    
    # 4 - document
    url(r'^document/(?P<doc_id>\d+)/$',
        operations.views.site.document, name='get_document'),

    url(r'^site/(?P<site_id>\d+)/document_duplicate_filter/$',
        operations.views.site.document_duplicate_filter, name='document_duplicate_filter'),
    url(r'^site/(?P<site_id>\d+)/document_reset_to_zero/$',
        operations.views.site.document_reset_to_zero, name='document_reset_to_zero'), 
    url(r'^site/(?P<site_id>\d+)/document_delete/$',
        operations.views.site.document_delete, name='document_delete'),
   
    # 5 - indexing
    url(r'^site/(?P<site_id>\d+)/es_index_site/$',
        operations.views.site.es_index_site, name='es_index_site'),

    url(r'^site/(?P<site_id>\d+)/es_remove_site_from_index/$',
        operations.views.site.es_remove_site_from_index, name='es_remove_site_from_index'),
    
    # tester
    url(r'^tester/$',operations.views.tester, name='tester'),
    url(r'^tester/(?P<query>[\w\ ]+)/(?P<testinggroup>\d+)/(?P<page>\d+)/$',operations.views.tester),
    url(r'^tester/(?P<query>\[\w ]+)/(?P<testinggroup>\d+)/$',operations.views.tester),
    url(r'^tester/(?P<query>\[\w\ ]+)/$',operations.views.tester)
]
    
    
    
    #url(r'^testing_input$',views.testing_input,name='testing_input'),
    #url(r'^testing$',views.testing,name='testing'),
