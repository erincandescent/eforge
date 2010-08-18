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

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from eforge import models
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
