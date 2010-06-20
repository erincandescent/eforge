# -*- coding: utf-8 -*-
# Create your views here.
from eforge import plugins
from eforge.models import Project
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext

def summary(request, proj_slug):
    project = get_object_or_404(Project, slug=proj_slug)
    return render_to_response('eforge/summary.html', {
        'project': project
    }, context_instance=RequestContext(request))

def about(request):
    return render_to_response('about.html', {
        'plugins': plugins.plugins
    }, context_instance=RequestContext(request))