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

from django.db import models
from django.core.urlresolvers import reverse
from eforge.models import Project
from eforge.update.models import Update, register_update_type
from eforge.vcs import project_repository

class Revision(models.Model):
        id_no       = models.AutoField(primary_key=True)
        id          = models.CharField(max_length=40, db_index=True)
        project     = models.ForeignKey(Project)
        parents     = models.ManyToManyField('self', related_name='children')
        date        = models.DateTimeField()
        
        @property 
        def vcs_revision(self):
            """ Revision object from the VCS plugin """
            if not getattr(self, '_vcs_revision', None):
                self._vcs_revision = project_repository(self.project).revision(self.id)
            return self._vcs_revision
            
        class Update:
            @classmethod
            def user(self, revision):
                return revision.author_user
            
            @classmethod
            def project(self, revision):
                return revision.project
                
            @classmethod
            def summary(self, revision):
                return 'Revision %s' % revision.short_id
            
            @classmethod
            def description(self, revision):
                return revision.message
                
            @classmethod
            def url(self, revision):
                return reverse('browser-revision', 
                    args=[revision.project.slug, revision.id])
            
            @classmethod
            def date(self, revision):
                return revision.date
register_update_type(Revision)

def _proxy_property(name):
    def _proxy(self):
        return getattr(self.vcs_revision, name)
    setattr(Revision, name, property(_proxy))

_proxy_property('short_id')
_proxy_property('author_email')
_proxy_property('author_name')
_proxy_property('author_user')
_proxy_property('message')
_proxy_property('short_message')
_proxy_property('root')