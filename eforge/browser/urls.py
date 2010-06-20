# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

patterns = patterns('eforge.browser.views',
    url('^(?P<commit>\w+)/(?P<path>.+)$',          'browse', name='browse-path'),
    url('^(?P<commit>\w+)/$',                      'browse', name='browse-revision'),
    url('^$',                                      'browse', name='browse-master'),
)