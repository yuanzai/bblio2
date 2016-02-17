from django.conf.urls import include, url
import search.views
import operations.urls
import testscrape.urls
import lau.views
from django.http import HttpResponse




urlpatterns = [

    #robots.txt
    url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")),

    #home page
    url(r'^$',lau.views.index),
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^testing_input/$',search.views.testing_input, name='testing_input'),
    url(r'^testing/$',search.views.testing, name='testing'),
    
    url(r'^autocomplete/', search.views.autocomplete, name='autocomplete'),
    url(r'^search/',search.views.index,name='index'),

    #Operations App
    url(r'^operations/',include('operations.urls', namespace='operations'),name='operations'),
    
    #TestScrape App - crawling tester site
    url(r'^testscrape/',include('testscrape.urls', namespace='scrape'),name='testscrape'),
    ]
