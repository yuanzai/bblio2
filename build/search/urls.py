from django.conf.urls import url
import views

urlpatterns = [ 
    #url(r'^$', views.scrape, name='scrape'),
    url(r'^(?P<site_id>\d+)/scraped/$',views.scraped,name='scraped'),
    url(r'^(?P<site_id>\d+)/delete/$',views.delete,name='delete'),
    #url(r'^testing_input$',views.testing_input,name='testing_input'),
    #url(r'^testing$',views.testing,name='testing'),
    ]
