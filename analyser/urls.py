from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^grafico2/$', views.index2, name='index2'),
    url(r'^plot/$', views.AjaxRequest, name='AjaxRequest'),
    url(r'^plot2/$', views.AjaxRequest2, name='AjaxRequest2')

]
