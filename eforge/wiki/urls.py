# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

patterns = patterns('eforge.wiki.views',
    url(r'^(?P<name>[a-zA-Z_/ ]+)$', 'wiki_page', name='wiki-page'),
    url(r'^$',                       'wiki_page', name='wiki-home'),
)