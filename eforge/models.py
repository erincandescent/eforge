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

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group, Permission
from django.db import models
import plugins
from operator import itemgetter

def logo_path(proj, name):
    return 'projects/%s_%s' % (proj.slug, name)

# Create your models here.
class Project(models.Model):
    slug          = models.SlugField(max_length=16, unique=True)
    name          = models.CharField(max_length=32, unique=True)
    repo_path     = models.CharField(max_length=64)
    description   = models.TextField()
    logo          = models.ImageField(upload_to=logo_path)
    members       = models.ManyToManyField(User,  related_name='projects', null=True, blank=True)
    member_groups = models.ManyToManyField(Group, related_name='projects', null=True, blank=True)
    parent        = models.ForeignKey('Project',  related_name='children', null=True, blank=True)
    def __unicode__(self):
        return self.name

    @property
    def topmenu(self):
        try:
            items = plugins.provider['mnu']
            return sorted([(reverse(i[0], args=[self.slug]), i[1]) for i in items.items()],
                            key=itemgetter(1))
        except Exception, e:
            print e

    class Meta:
        permissions = (
            ('manage', 'Can manage the project'),
        )

class Milestone(models.Model):
    project     = models.ForeignKey(Project)
    previous    = models.OneToOneField('Milestone', related_name='next', blank=True, null=True)
    name        = models.CharField(max_length=32)
    description = models.TextField()
    due_date    = models.DateTimeField()
    completed   = models.BooleanField()

    def __unicode__(self):
        return self.name

class UserPermission(models.Model):
    user       = models.ForeignKey(User, null=True)
    project    = models.ForeignKey(Project)
    permission = models.ForeignKey(Permission)

class GroupPermission(models.Model):
    group      = models.ForeignKey(Group)
    project    = models.ForeignKey(Project)
    permission = models.ForeignKey(Permission)

"""
    anon = user.is_anonymous()
    for backend in auth.get_backends():
        if not anon or backend.supports_anonymous_user:
            if hasattr(backend, "has_perm"):
                if obj is not None:
                    if (backend.supports_object_permissions and
                    backend.has_perm(user, perm, obj)):
                        return True
                        else:
                            if backend.has_perm(user, perm):
                                return True
                                return False
"""

def group_has_project_perm(group, project, perm):
    if group.has_perm(perm):
        return True

    if project.grouppermission_set.filter(group=group, permission=perm).count():
        return True
    return False

def user_has_project_perm(user, project, perm):
    if user.has_perm(perm):
        return True

    if project.userpermission_set.filter(user=user, permission=perm).count():
        return True

    for group in user.groups.all():
        if group_has_project_perm(group, project, perm):
            return True

    return False

User.has_project_perm = user_has_project_perm
Group.has_project_perm = group_has_project_perm