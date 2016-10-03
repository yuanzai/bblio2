from django.conf.urls import url
import emplifive.views

urlpatterns = [
    url(r'^$', 'emplifive.views.index',name='index'),
]

