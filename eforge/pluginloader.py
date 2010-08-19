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

from django.conf import settings
import sys
from plugins import *

for app in settings.INSTALLED_APPS:
    __import__(app)
    mod = sys.modules[app]

    if 'EFORGE_PLUGIN' in dir(mod):
        print ">> plugin %s" % app
        plugin = mod.EFORGE_PLUGIN
        plugin['module'] = app

        plugins.append(plugin)

for plugin in plugins:
    if 'provides' not in plugin:
        continue

    for ifc in plugin['provides']:
        objs = plugin['provides'][ifc]

        if ifc in provider:
            provider[ifc].update(dict(objs))
        else:
            provider[ifc] = dict(objs)
