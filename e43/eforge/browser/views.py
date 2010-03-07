from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from pygments.lexers import guess_lexer_for_filename
from pygments import highlight
from pygments.formatters import HtmlFormatter

from e43.eforge.models import Project
import git

def browse(request, proj_slug, commit = 'master', path = ''):
    project = get_object_or_404(Project, slug=proj_slug)
    repo    = git.Repo(project.repo_path)
    gcommit = repo.commit(commit)
    tree    = gcommit.tree

    file = tree
    if len(path):
        for i in path.split('/'):
            file   = file.get(i)

    if not hasattr(file, 'data'): # Hack - but no better way?
        return render_to_response('browser/directory.html', {
            'project':   project,
            'repo':      repo,
            'commit':    commit,
            'gcommit':   gcommit,
            'directory': file,
            'path':      path,
        }, context_instance=RequestContext(request))
    else:
        lexer       = guess_lexer_for_filename(file.basename, file.data)
        formatter   = HtmlFormatter(linenos=True, cssclass='source')
        highlighted = highlight(file.data, lexer, formatter)

        return render_to_response('browser/file.html', {
            'project':     project,
            'repo':        repo,
            'commit':      commit,
            'gcommit':     gcommit,
            'file':        file,
            'styles':      formatter.get_style_defs(),
            'highlighted': highlighted,
        }, context_instance=RequestContext(request))
