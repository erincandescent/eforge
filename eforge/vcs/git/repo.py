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

import dulwich
import StringIO
from datetime import datetime
from eforge.vcs.interface import *
from eforge.vcs.git.models import RevisionRelation

class GitRepository(IRepository):
    def __init__(self, path):
        self.repo = dulwich.repo.Repo(path)

    def __findrefs(self, prefix):
        grefs = self.repo.refs
        refs = {}
        for ref in grefs.keys():
            if ref.startswith(prefix):
                ## Ugly ugly ugly! Gotta be a better way!
                gref = self.repo[self.repo.refs[ref]]
                if isinstance(gref, dulwich.objects.Tag):
                    obj = gref.object
                else:
                    obj = gref
                if isinstance(obj, tuple):
                    # What the? Why are these in
                    #  (type, str(sha)) form?! What?!
                    obj = self.repo[obj[1]]
                refs[ref[len(prefix):]] = GitRevision(self, obj)
        return refs

    @property
    def branches(self):
        return self.__findrefs('refs/heads/')

    @property
    def tags(self):
        return self.__findrefs('refs/tags/')

    def revision(self, id):
        return GitRevision(self, id)

    @property
    def head(self):
        return GitRevision(self, self.repo.head())

    def revisions(self, num):
        revs = []
        seen = set()

        walk = self.repo.get_graph_walker()
        ob = walk.next()
        while ob and len(revs) < num:
            if not ob in seen:
                seen.add(ob)
                revs.append(GitRevision(self, ob))
            ob = walk.next()

        return revs

class GitRevision(IRevision):
    def __init__(self, repo, rev):
        self.repo = repo
        if not isinstance(rev, dulwich.objects.Commit):
            self.rev  = repo.repo[rev]
        else:
            self.rev = rev

        if not RevisionRelation.objects.filter(child=self.id).count():
            # No cache built, we should make one
            for revision in self.parents:
                rel = RevisionRelation(child=self.id, parent=revision.id)
                rel.save()

    @property
    def id(self):
        return self.rev.id


    @property
    def short_id(self):
        return self.id[0:8]

    @property
    def author_email(self):
        try:
            return self.rev.author.split('<')[1][:-1]
        except:
            return None

    @property
    def message(self):
        return self.rev.message

    @property
    def author_name(self):
        try:
            return self.rev.author.split('<')[0].strip()
        except:
            return self.rev.author

    @property
    def parents(self):
        return [GitRevision(self.repo, x) for x in self.rev.parents]

    @property
    def root(self):
        return GitDirectory(self.repo, self.repo.repo[self.rev.tree], None, None)
        
    @property
    def date(self):
        return datetime.utcfromtimestamp(self.rev.commit_time)

class GitDirectory(IDirectory):
    def __init__(self, repo, tree, parent, name):
        self.repo = repo
        self.tree = tree
        IDirectory.__init__(self, parent, name)

    @property
    def children(self):
        children = []
        entries = self.tree.entries()
        print 'children %s' % entries
        for ent in entries:
            print ent
            name = ent[1]
            obj  = self.repo.repo[ent[2]]
            print obj
            try:
                if isinstance(obj, dulwich.objects.Tree):
                    children.append(GitDirectory(self.repo, obj, self, name))
                else:
                    children.append(GitFile(self.repo, obj, self, name))
            except Exception, e:
                print "Exception: %s" % e

        return children

    def child(self, name):
        obj = self.repo.repo[self.tree[name][1]]
        if isinstance(obj, dulwich.objects.Tree):
            return GitDirectory(self.repo, obj, self, name)
        else:
            return GitFile(self.repo, obj, self, name)

class GitFile(IFile, StringIO.StringIO):
    def __init__(self, repo, file, parent, name):
        self.repo = repo
        self.file = file

        self.data = file.data

        IFile.__init__(self, parent, name)
        StringIO.StringIO.__init__(self, self.data)
        self.__size = len(self.data)

    @property
    def size(self):
        return self.__size

