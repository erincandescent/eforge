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

from django import forms
from django.http import HttpResponse
from eforge.models import Project
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from eforge import plugins

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ('slug', 'repo_path', 'members', 'member_groups')

def project(request, project):
    updated = False
    if request.method == 'POST':
        project_form = ProjectForm(request.POST, request.FILES, instance=project,
                                   prefix='proj')
        if project_form.is_valid():
            project_form.save()
            updated = True
    else:
        project_form = ProjectForm(instance=project, prefix='proj')

    return render_to_response('eforge/manage_project.html', {
        'project':      project,
        'form':         project_form,
        'updated':      updated,
    }, context_instance=RequestContext(request))

def get_permission(model, code):
    ct = ContentType.objects.get_for_model(model)
    return Permission.objects.get(content_type=ct, codename=code)

#
# Returns:
# {
#   'Title': [
#     Permisison(), Permission(), ...
#   ]
# }
def permission_list():
    dict = {}
    for group in plugins.provider['perms'].itervalues():
        title = group['title']
        perms = group['perms']
        list = []
        for perm in perms:
            list.append(get_permission(*perm))
        dict[title] = list
    return dict

def members(request, project):
    if 'a' in request.GET:
        act = request.GET['a']
        group = None
        user  = None
        obj   = None

        if act == 'g':
            group = Group.objects.get(pk=request.GET['g'])
            obj   = group
        else:
            user = User.objects.get(pk=request.GET['u'])
            obj  = user

        return render_to_response('eforge/manage_member.html', {
            'project':      project,
            'user':         user,
            'group':        group,
            'obj':          obj,
            'perms':        permission_list(),
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('eforge/manage_members.html', {
            'project':      project,
        }, context_instance=RequestContext(request))