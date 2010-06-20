# -*- coding: utf-8 -*-
import urls
from eforge.menu import ItemOrder

EFORGE_PLUGIN = {
    'name':     'Repository Browser',
    'credit':   'Copyright &copy; 2010 Element43 and contributors',
    
    'provides': {
        'app': [('browser',       urls.patterns)],
        'mnu': [('browse-master', ItemOrder(300, 'Browse source'))],
    },
}