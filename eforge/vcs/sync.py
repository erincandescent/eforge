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

from eforge.models import Project
from eforge.vcs.models import Revision
from eforge.vcs import project_repository

def sync_project(project):
    """
        Synchronizes the revision cache with the project's repository. Working backwards from all the repository heads (defined as the current branches and tags), we import all revisions until we find one in the database.
    """
    
    print "== Synchronizing project %s" % project.name
    repo = project_repository(project)
    
    for name, rev in repo.branches.items():
        print "-- Branch %s" % name
        import_revision(project, rev)
        
    for name, rev in repo.tags.items():
        print "-- Tag %s" % name
        import_revision(project, rev)
        
def import_revision(project, rev):
    try:
        return Revision.objects.get(id=rev.id)
    except Revision.DoesNotExist, e:
        pass
        
    print "Importing %s (%s)" % (rev.id, rev.date)
    
    parents = []
    for parent in rev.parents:
        parents.append(import_revision(project, parent))
        
    dbrev = Revision(project=project, id=rev.id, date=rev.date)
    dbrev.save()
    dbrev.parents = parents
    dbrev.save()
    return dbrev