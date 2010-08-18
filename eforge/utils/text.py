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
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
import re

#
# All of the text match operators in here should fail nondestructively.
# In other words, wrap your code in
# try:
#    ..my code here..
# except:
#    return match
#
# blocks, so that if some unexpected input occurs, you don't kill the page and
# just degrade gracefully.
#
# Remember: We are already dealing with HTML encoded data! No need to worry
# about HTML injection in that regard.
#

bold      = re.compile(r'\*\*(.*?)\*\*')
italic    = re.compile(r'//(.*?)//')
underline = re.compile(r'__(.*?)__')
buglink   = re.compile(r'[#][\w]+-[\d]+')
wikilink  = re.compile(r'\[\[[\w ]+\]\]')
freelink  = re.compile(r'[\w]+://[\w?&;./=]+')

def bugmatch(match):
    try:
        match = match.group()
        proj, bug = match[1:].split('-')
        proj = proj.lower()
        url = reverse('bug-show', args=[proj, bug])
        return "<a href='%s'>%s</a>" % (url, match)
    except:
        return match

def wikimatcher(proj):
    def wikimatch(match):
        try:
            match = match.group()
            page = match[2:-2]
            page = page.replace(' ', '_')
            page = page[0].upper() + page[1:]
            url = reverse('wiki-page', args=[proj.slug, page])
            return "<a href='%s'>%s</a>" % (url, match)
        except:
            return match
    return wikimatch

def linkmatch(match):
    try:
        match = match.group()
        postfix = ''
        if match[-1] == '.':
            postfix = '.'
            match = match[:-1]
        return "<a href='%s'>%s</a>%s" % (match, match, postfix)
    except:
        return match

def textscan(project, instr):
    '''
    Plain text scanner & formatter

    Takes some plain text, and applies some useful formatting to it. This is
    non-disruptive formatting - it will not cause the text to be reflowed,
    and will preserve any manual spacing that the text assumed.

    The markup language used is very Creole-like - **bold** and //italics//,
    for example. Links are done by [[Wiki Page]]. Bugs are linked by #EFORGE-32,
    etc.
    '''
    # HTML encode the text
    instr = escape(instr)

    # Output line buffer list
    # (Pushing onto a list and joining at the end is faster, and doesn't really
    # make things any more complex)
    linebuf = []

    wikimatch = wikimatcher(project)

    # We work on text a line at a time. This produces pretty decent results for
    # most text.    tokmatch
    lines = instr.split('\n')
    for line in lines:
        # Handle the simple formatting
        line = bold.sub(r'<b>\1</b>', line)
        line = italic.sub(r'<i>\1</i>', line)
        line = underline.sub(r'<u>\1</u>', line)

        # Now more complex - links!
        line = buglink.sub(bugmatch, line)
        line = wikilink.sub(wikimatch, line)
        line = freelink.sub(linkmatch, line)

        linebuf.append(line)

    print linebuf
    rv = mark_safe('<br />'.join(linebuf))
    print "!!%s!!" % rv
    return rv