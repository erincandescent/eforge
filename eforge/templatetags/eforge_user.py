# -*- coding: utf-8 -*-
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
