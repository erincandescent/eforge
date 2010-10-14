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

from django import template
from django.contrib.auth.models import User
import hashlib
from urllib import urlencode
register = template.Library()

@register.filter(name='gravatar')
def gravatar(user, size=None):
    email = None
    if isinstance(user, User):
        email = user.email.lower()
    else:
        email = user.lower()

    hash = hashlib.md5(email).hexdigest()
    url = 'http://www.gravatar.com/avatar/%s' % hash
    if size:
        url += '?%s' % urlencode({'s': size})
    return url

@register.tag(name='has_project_perm')
def has_project_perm(parser, token):
    try:
        tag_name, var, member, project, perm = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires four arguments" % token.contents.split()[0]
    return HasProjectPermNode(var, member, project, perm)
    
class HasProjectPermNode(template.Node):
    def __init__(self, var, member, project, perm):
        self.var = var
        self.member  = template.Variable(member)
        self.project = template.Variable(project)
        self.perm    = template.Variable(perm)
        
    def render(self, context):
        try:
            member = self.member.resolve(context)
            project = self.project.resolve(context)
            perm = self.perm.resolve(context)
            
            state = member.has_project_perm(project, perm)
            context[self.var] = state
            return ''
        except template.VariableDoesNotExist:
            return ''