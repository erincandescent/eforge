# -*- coding: utf-8 -*-
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
