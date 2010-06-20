# -*- coding: utf-8 -*-
import urls
from eforge.menu import ItemOrder

EFORGE_PLUGIN = {
    'name':     'Issue Tracker',
    'credit':   'Copyright &copy; 2010 Element43 and contributors',
    
    'provides': {
        'app': [('tracker', urls.patterns)],
        'mnu': [('bug-list', ItemOrder(200, 'Tracker'))],
    },
}