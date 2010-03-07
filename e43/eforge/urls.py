from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic import list_detail
import models
project_list_info = { 
    'template_name': 'eforge/project_list.html',
    'queryset': models.Project.objects.all(),
}

projpatterns = patterns('e43.eforge.views',
    url(r'^wiki/(?P<name>[a-zA-Z_/ ]+)$', 'wiki_page', name='wiki-page'),
    url(r'^wiki/$',                       'wiki_page', name='wiki-home'),
    url(r'^$',                            'wiki_page', name='project-page'),
)

projpatterns += patterns('e43.eforge.bugs.views',
    url(r'^tracker/(?P<bug_id>\d+)$', 'showbug', name='bug-show'),
    url(r'^tracker/new$',             'newbug', name='bug-new'),
    url(r'^tracker/attachment/(?P<attach_id>\d+)$', 'attachment', name='bug-attachment'),
    url(r'^tracker/$',                'listbugs', name='bug-list'),
)

projpatterns += patterns('e43.eforge.browser.views',
    url('^browse/(?P<commit>\w+)/(?P<path>.+)$',          'browse', name='browse-path'),
    url('^browse/(?P<commit>\w+)/$',                      'browse', name='browse-revision'),
    url('^browse/$',                                      'browse', name='browse-master'),
)

urlpatterns = patterns('',
    url(r'^(?P<proj_slug>\w+)/' , include(projpatterns)),
    url(r'^$', list_detail.object_list, project_list_info, name='project-list'),
)
