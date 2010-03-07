# Create your views here.
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
import models
from TCWiki import views as WViews

def wiki_page(request, proj_slug, name='Main_page'):
    project = get_object_or_404(models.Project, slug=proj_slug)
    wiki_info = {
        'pageloc': (lambda page: reverse('wiki-page', args=[proj_slug, page])),
        'wiki_id': project.id,
        'pslug':   project.slug,
        'project': project,
        'context': {'project': project},
    }
    return WViews.page(request, name, wiki_info=wiki_info)
