from django import template
import hashlib
from urllib import urlencode
register = template.Library()

@register.filter('gravatar', gravatar)
def gravatar(user, size=None):
    hash = hashlib.md5(user.email.lower()).hexdigest()
    url = 'http://www.gravatar.com/avatar/%s' % hash
    if size:
        url += '?%s' % urlencode({'s': size})
    return url
gravatar.needs_autoescape = True
