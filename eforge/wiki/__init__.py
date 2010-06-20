# -*- coding: utf-8 -*-
import urls
from eforge.menu import ItemOrder

EFORGE_PLUGIN = {
    'name':     'Wiki',
    'credit':   'Copyright &copy; 2010 Element43 and contributors. '
                'Powered by TCWiki.',
    
    'provides': {
        'app': [('wiki',      urls.patterns)],
        'mnu': [('wiki-home', ItemOrder(100, 'Wiki'))],
    },
}