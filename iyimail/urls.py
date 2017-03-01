__author__ = 'koray'

from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^(?P<ruleID>\d+)/$', preview, name='rule-preview'),
]