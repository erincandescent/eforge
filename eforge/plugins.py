# -*- coding: utf-8 -*-
from django.conf import settings
import sys

plugins   = []
provider = {}

for app in settings.INSTALLED_APPS:
    print app
    __import__(app)
    mod = sys.modules[app]

    if 'EFORGE_PLUGIN' in dir(mod):
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
