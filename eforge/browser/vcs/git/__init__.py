# -*- coding: utf-8 -*-
import repo

EFORGE_PLUGIN = {
    'name':     'Git Repository Browser',
    'credit':   'Copyright &copy; 2010 Element43 and contributors',

    'provides': {
        'vcs': [('git',    repo.GitRepository)],
    },
}