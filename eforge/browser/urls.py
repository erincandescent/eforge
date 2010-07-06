# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

patterns = patterns('eforge.browser.views',
    url('^file/(?P<commit>\w+)/$',                     'file',     name='browse-rootdir'),
    url('^file/(?P<commit>\w+)/(?P<path>.*)$',         'file',     name='browse-path'),
    url('^rev/(?P<commit>\w+)/$',                      'revision', name='browse-revision'),
    url('^$',                                          'history',  name='browse-master'),
)