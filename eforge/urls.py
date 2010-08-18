# -*- coding: utf-8 -*-
# EForge project management system, Copyright © 2010, Element43
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic import list_detail
import models
import plugins

project_list_info = {
    'template_name': 'eforge/project_list.html',
    'queryset': models.Project.objects.all(),
}

projpatterns = patterns('eforge.views',
    url(r'^$',                            'summary', name='project-page'),
)

for k in plugins.provider['app']:
    projpatterns += patterns('',
        url('^%s/' % k, include(plugins.provider['app'][k]))
    )

urlpatterns = patterns('',
    url(r'^p/(?P<proj_slug>\w+)/' , include(projpatterns)),
    url(r'^p/$', list_detail.object_list, project_list_info, name='project-list'),
    url(r'^eforge/about$', 'eforge.views.about', name='about-eforge')
)
