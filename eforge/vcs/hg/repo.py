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

import StringIO
from eforge.browser.interface import *
from mercurial.node import short
from mercurial.ui import ui
from mercurial.localrepo import localrepository
from mercurial.util import shortuser, email
from subprocess import Popen, PIPE
from binascii import unhexlify

class HgRepository(IRepository):
    def __init__(self, path):
        self.ui   = ui()
        self.repo = localrepository(self.ui, path)
        self.path = path

    @property
    def branches(self):
        b = {}
        for tag, revid in self.repo.branchtags().items():
            b[tag] = HgRevision(self, revid)
        return b

    @property
    def tags(self):
        b = {}
        for tag, revid in self.repo.tags().items():
            b[tag] = HgRevision(self, revid)
        return b

    def revision(self, id):
        try:
            return HgRevision(self, unhexlify(id))
        except:
            raise ValueError("Invalid ID %s" % id)

    @property
    def head(self):
        return HgRevision(self, self.repo.changelog.tip())

    def revisions(self, num):
        revs = []

        log = self.repo.changelog
        seen = set()
        heads = log.heads()
        edges = []

        while heads:
            hgrev = HgRevision(self, heads.pop())
            seen.add(hgrev.id)
            edges.append(hgrev)

        while edges and len(revs) < num:
            rev = edges.pop()
            revs.append(rev)

            for p in rev.parents:
                if not p.id in seen:
                    edges.append(p)
                    seen.add(p.id)

        return revs


class HgRevision(IRevision):
    def __init__(self, repo, rev):
        self.repo = repo
        if isinstance(rev, str):
            self.rev  = repo.repo[rev]
        else:
            self.rev  = rev

    @property
    def id(self):
        return self.rev.hex()


    @property
    def short_id(self):
        return short(self.rev.node())

    @property
    def author_email(self):
        return email(self.rev.user())

    @property
    def author_name(self):
        return shortuser(self.rev.user())

    @property
    def message(self):
        return self.rev.description()

    @property
    def parents(self):
        if self.rev.rev() == 0:
            return []

        return [HgRevision(self.repo, x) for x in self.rev.parents()]

    @property
    def children(self):
        return [HgRevision(self.repo, x) for x in self.rev.children()]

    @property
    def root(self):
        mf = self.rev.manifest()

        dirs  = { '': HgDirectory(self.repo, self, None, None) }

        def rec_add(dir):
            obj = None

            par = dirs['']
            name = dir
            if '/' in dir:
                pardir, name = dir.rsplit('/', 1)
                par = rec_add(pardir)

            if dir in dirs:
                obj = dirs[name]
            else:
                obj = dirs[name] = HgDirectory(self.repo, self, par, name)

            par._children[name] = obj
            return obj

        for k in mf.keys():
            dir = ''
            name = k
            obj = dirs['']
            if '/' in k:
                dir, name = k.rsplit('/', 1)
                obj = rec_add(dir)

            obj._children[name] = HgFile(self.repo, self, obj, name, k)

        return dirs['']


class HgDirectory(IDirectory):
    def __init__(self, repo, rev, parent, name):
        IDirectory.__init__(self, parent, name)
        #print "md %s" % self.path
        self.repo      = repo
        self.rev       = rev
        self._children = {}

    @property
    def children(self):
        return self._children.values()

    def child(self, name):
        return self._children[name]

class HgFile(IFile, StringIO.StringIO):
    def __init__(self, repo, rev, parent, name, path):
        IFile.__init__(self, parent, name)
        #print "mf %s" % self.path
        self.repo = repo
        self.rev  = rev
        self.file = rev.rev[path]
        self.__initialized = False

    def __lazyinit(self):
        self.__data = self.file.data()
        StringIO.StringIO.__init__(self, self.__data)
        self.__size = len(self.__data)
        self.__initialized = True

    @property
    def data(self):
        if not self.__initialized:
            self.__lazyinit()
        return self.__data

    @property
    def size(self):
        if not self.__initialized:
            self.__lazyinit()
        return self.__size

    def open(self):
        if not self.__initialized:
            self.__lazyinit()

