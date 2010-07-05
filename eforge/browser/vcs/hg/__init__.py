# -*- coding: utf-8 -*-
import repo

EFORGE_PLUGIN = {
    'name':     'Mercurial Repository Browser',
    'credit':   'Copyright &copy; 2010 Element43 and contributors',

    'provides': {
        'vcs': [('hg',    repo.HgRepository)],
    },
}