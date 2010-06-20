# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from pygments.lexers import guess_lexer_for_filename, TextLexer
from pygments import highlight
from pygments.formatters import HtmlFormatter

from eforge.models import Project
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

def browse(request, proj_slug, commit = None, path = ''):
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
                lexer = guess_lexer_for_filename(obj.name, obj.data)
            except:
                lexer = TextLexer()
            formatter   = HtmlFormatter(linenos=True, cssclass='source')
            highlighted = highlight(obj.data, lexer, formatter)
            styles    = formatter.get_style_defs()
        
        return render_to_response('browser/file.html', {
            'project':     project,
            'repo':        repo,
            'commit':      commit,
            'ncommit':     ncommit,
            'file':        obj,
            'styles':      styles,
            'highlighted': highlighted,
        }, context_instance=RequestContext(request))