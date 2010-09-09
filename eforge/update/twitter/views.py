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
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from eforge.decorators import project_page, has_project_perm
from eforge.update.twitter.models import Token
from twitter import Twitter, OAuth, TwitterHTTPError
import urlparse

consumer_key    = settings.TWITTER_CONSUMER_KEY
consumer_secret = settings.TWITTER_CONSUMER_SECRET
authorize_url   = 'https://api.twitter.com/oauth/authorize?oauth_token=%s'
    
def abs_reverse(*args, **kwargs):
    domain = "http://%s" % Site.objects.get_current().domain
    return urlparse.urljoin(domain, reverse(*args, **kwargs))

@project_page
@has_project_perm('eforge.manage')
def setup(request, project):
    twitter = Twitter(
        auth=OAuth('', '', consumer_key, consumer_secret), 
        format='', secure=True,)
    
    tokens = urlparse.parse_qs(
        twitter.oauth.request_token(
            oauth_callback=abs_reverse('twitter-callback', args=[project.slug])
        ))
    
    print tokens
    
    request.session['oauth_secret'] = tokens['oauth_token_secret'][0]
    
    return redirect(authorize_url % tokens['oauth_token'][0])
    
@project_page
@has_project_perm('eforge.manage')
def callback(request, project):
    oauth_token    = request.GET['oauth_token']
    oauth_verifier = request.GET['oauth_verifier']
    oauth_secret   = request.session['oauth_secret']

    print request.session.items()

    twitter = Twitter(
        auth=OAuth(oauth_token, oauth_secret, consumer_key, consumer_secret),
        format='', secure=True,)
    
    try:
        tokens = urlparse.parse_qs(
            twitter.oauth.access_token(oauth_verifier=oauth_verifier))
    except TwitterHTTPError, e:
        print e
        raise
        
    try:
        token = Token.objects.get(project=project)
    except Token.DoesNotExist:
        token = Token(project=project)
    
    token.token        = tokens['oauth_token'][0]
    token.token_secret = tokens['oauth_token_secret'][0]
    token.user         = tokens['screen_name'][0]
    token.save()
    
    return render_to_response('twitter/done.html', {
        'name': tokens['screen_name'][0]
    }, context_instance=RequestContext(request))