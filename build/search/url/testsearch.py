from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^(?P<query>\S+)/$',views.testsearch,name='testeearch'),
    url(r'^(?P<query>\S+)/(?P<page>\d+/$',views.testsearch,name='testsearchpage'),
)
