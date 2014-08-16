#Copyright (c) Adam Kurkiewicz 2014, all rights reserved.
from django.conf.urls import patterns, url

from website import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^play$', views.play),
    url(r'^exchangeCommitments$', views.exchangeCommitments),
    url(r'^exchangeSecrets$', views.exchangeSecrets),
    url(r'^get_board$', views.get_board),
    url(r'^login$', views.login),
    url(r'^signin$', views.signin),
    url(r'^signup$', views.signup),
    url(r'^get_user$', views.get_user),
    #url(r'^negotiate_first', views.negotiate_first),
    #url(r'^negotiate_second', views.negotiate_second),
    url(r'^register$', views.register),
    url(r'^signout$', views.logout)
)
