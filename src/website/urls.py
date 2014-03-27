from django.conf.urls import patterns, url

from website import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^play$', views.play)
)
