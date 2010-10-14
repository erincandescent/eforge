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

from eforge.models import Project
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.contrib.auth.models import User, Group
from django.utils.decorators import available_attrs
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import urlquote
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from functools import wraps

def project_page(view):
    def wrapper(request, proj_slug, *args, **kwargs):
        project = get_object_or_404(Project, slug=proj_slug)
        return view(request, project, *args, **kwargs)
    return wrapper

def user_page(view):
    def wrapper(request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        return view(request, user, *args, **kwargs)
    return wrapper

def group_page(view):
    def wrapper(request, groupname, *args, **kwargs):
        group = get_object_or_404(Group, name=groupname)
        return view(request, group, *args, **kwargs)
    return wrapper

def _proj_user_passes_test(test_func, login_url=None,
                     redirect_field_name=REDIRECT_FIELD_NAME):
    """
        Decorator for views that checks that the user passes the given test,
        returning a 400 (not authorized) error or redirecting to login as
        appropriate.

        This is much like Django's version, except it is project aware
    """
    if not login_url:
        from django.conf import settings
        login_url = settings.LOGIN_URL

        def decorator(view_func):
            def _wrapped_view(request, project, *args, **kwargs):
                if test_func(request.user, project):
                    return view_func(request, project, *args, **kwargs)
                elif request.user.is_authenticated():
                    tmpl = get_template('400.html')
                    return HttpResponseForbidden(
                        tmpl.render(RequestContext(request, {})))
                else:
                    path = urlquote(request.get_full_path())
                    tup = login_url, redirect_field_name, path
                    return HttpResponseRedirect('%s?%s=%s' % tup)
            return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
        return decorator

def has_project_perm(perm, *args, **kwargs):
    return _proj_user_passes_test(
        lambda u, p: u.has_project_perm(p, perm),
        *args, **kwargs)
