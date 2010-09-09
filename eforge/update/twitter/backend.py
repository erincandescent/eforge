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

from django.contrib.auth.models import User
from eforge.update.models import Update
from eforge.update.twitter.models import Token
from django.conf import settings
from django.contrib.sites.models import Site
from urllib2 import urlopen, HTTPError
from urllib  import quote_plus
from twitter import Twitter, OAuth, TwitterError
import urlparse

def abs_reverse(*args, **kwargs):
    domain = "http://%s" % Site.objects.get_current().domain
    return urlparse.urljoin(domain, reverse(*args, **kwargs))
    
def abs_url(url):
    if url.startswith('http:'):
        return url
    else:
        domain = "http://%s" % Site.objects.get_current().domain
        return urlparse.urljoin(domain, url)

try:
    consumer_key    = settings.TWITTER_CONSUMER_KEY
    consumer_secret = settings.TWITTER_CONSUMER_SECRET
except:
    print "== eforge.update.twitter =="
    print "You need to specify your TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET"
    print "If you haven't, go register your install as a Twitter app"
    raise
    
    
isgd = 'http://is.gd/api.php?longurl=%s'
def send(update):
    token = Token.objects.get(project=update.project)
    
    url = isgd % quote_plus(abs_url(update.url))
    try:
        fd = urlopen(url)
        short = fd.read()
    except HTTPError, e:
        print 'is.gd. error %s (url %s)' % (e, url)
        short = ''
    
    maxlen = 140 - len(update.user.username) - len(short) - 3
    
    msg = u'%s: %s %s' % (update.user.username, update.summary[0:maxlen], short)
    try:
        twitter = Twitter(
            auth=OAuth(token.token, token.token_secret, 
                       consumer_key, consumer_secret),
            secure=True,
            api_version='1',
            domain='api.twitter.com')
                   
        twitter.statuses.update(status=msg.encode('utf-8', 'replace'))
    except TwitterError, e:
        print e
        raise
