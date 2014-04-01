from django.conf.urls import patterns, url

from website import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^play$', views.play),
    url(r'^nextmove$', views.nextmove),
    url(r'^get_board$', views.get_board),

)
