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

from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from pygments.lexers import guess_lexer_for_filename, TextLexer
from pygments import highlight
from pygments.formatters import HtmlFormatter
from eforge.models import Project
from eforge.utils.text import textscan
from eforge import plugins

def plugin_for(path):
    vcs, path = path.split(':', 1)

    return plugins.provider['vcs'][vcs](path)

def descend_tree(repo, tree, path):
    #try:
        obj = tree
        for i in path.split('/'):
            if len(i) == 0:
                continue

            if obj.is_file:
                raise Http404

            obj = obj.child(i)
        return obj
    #except:
    #    raise Http404

def history(request, proj_slug):
    project = get_object_or_404(Project, slug=proj_slug)
    repo = plugin_for(project.repo_path)

    start = 0
    num   = 50
    if 's' in request.GET:
        start = int(request.GET['s'])
    if 'n' in request.GET:
        num = int(request.GET['n'])
    end = start + num

    revisions = repo.revisions(end + 1)
    end = min(end, len(revisions))
    prev = max(0, start - num)

    return render_to_response('browser/history.html', {
        'project':   project,
        'repo':      repo,
        'revisions': revisions[start:end],
        'is_end':    (end >= len(revisions)),
        'is_start':  (start == 0),
        'start':     start+1,
        'next':      end,
        'num':       num,
        'prev':      prev,
    }, context_instance=RequestContext(request))

def file(request, proj_slug, commit = None, path = ''):
    project = get_object_or_404(Project, slug=proj_slug)
    #try:
    repo = plugin_for(project.repo_path)
    #except:
    #    raise Http404

    if commit is None:
        ncommit = repo.head
        commit  = ncommit.id
    else:
        ncommit = repo.revision(commit)

    tree = ncommit.root
    obj  = descend_tree(repo, tree, path)
    if obj.is_directory:
        return render_to_response('browser/directory.html', {
            'project':   project,
            'repo':      repo,
            'commit':    commit,
            'ncommit':   ncommit,
            'directory': obj,
            'path':      path,
        }, context_instance=RequestContext(request))
    else:
        lexer = None
        formatter = None
        highlighted = None
        styles = ''
        if obj.is_text:
            try:
                lexer = guess_lexer_for_filename(obj.name, obj.data,
                       		encoding=obj.text_encoding or 'chardet')
            except:
                lexer = TextLexer(encoding=obj.text_encoding or 'chardet')
            formatter   = HtmlFormatter(linenos=True, cssclass='source')
            highlighted = highlight(obj.data, lexer, formatter)
            styles      = formatter.get_style_defs()

        return render_to_response('browser/file.html', {
            'project':     project,
            'repo':        repo,
            'commit':      commit,
            'ncommit':     ncommit,
            'file':        obj,
            'styles':      styles,
            'highlighted': highlighted,
        }, context_instance=RequestContext(request))

def revision(request, proj_slug, commit):
    project = get_object_or_404(Project, slug=proj_slug)
    repo = plugin_for(project.repo_path)

    ncommit = repo.revision(commit)

    return render_to_response('browser/revision.html', {
            'project':     project,
            'repo':        repo,
            'commit':      commit,
            'rev':         ncommit,
            'description': textscan(project, ncommit.message),
    }, context_instance=RequestContext(request))