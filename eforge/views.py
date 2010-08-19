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

# Create your views here.
from eforge import plugins
from eforge.models import Project
from eforge.decorators import project_page
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext

@project_page
def summary(request, project):
    return render_to_response('eforge/summary.html', {
        'project': project
    }, context_instance=RequestContext(request))

def about(request):
    import platform
    import django
    import eforge

    return render_to_response('eforge/about.html', {
        'plugins':      plugins.plugins,
        'eforgever':    eforge.get_version(),
        'djangover':    django.get_version(),
        'pyver':        platform.python_version(),
    }, context_instance=RequestContext(request))
