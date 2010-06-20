# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

patterns = patterns('eforge.bugs.views',
    url(r'^(?P<bug_id>\d+)$', 'showbug', name='bug-show'),
    url(r'^new$',             'newbug', name='bug-new'),
    url(r'^attachment/(?P<attach_id>\d+)$', 'attachment', name='bug-attachment'),
    url(r'^$',                'listbugs', name='bug-list'),
)