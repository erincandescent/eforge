# -*- coding: utf-8 -*-
from django.db import models
from eforge.models import Project
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
import os.path

class Component(models.Model):
    project = models.ForeignKey(Project)
    name    = models.CharField(max_length=32)
    def __unicode__(self):
        return self.name

IssuePriority = (
    (1, 'Security Vulnerability'),
    (2, 'Critical'),
    (3, 'High'),
    (4, 'Medium'),
    (5, 'Low'),
)

IssueType = (
    (1, 'Bug'),
    (2, 'Feature Request'),
    (3, 'Patch'),
)

class Bug(models.Model):
    project    = models.ForeignKey(Project)
    component  = models.ForeignKey(Component)
    priority   = models.SmallIntegerField(choices=IssuePriority, default=4)
    issue_type = models.SmallIntegerField(choices=IssueType, default=1)
    title      = models.CharField(max_length=50)
    
    submitter  = models.ForeignKey(User, related_name='submitted_bugs')
    owner      = models.ForeignKey(User, related_name='owned_bugs', blank=True)

    depends    = models.ManyToManyField('self', symmetrical=False, related_name='blocks', blank=True)
    
    watchers   = models.ManyToManyField(User, related_name='watching_bugs', blank=True)

    @property
    def issue_type_name(self):
        return IssueType[self.issue_type-1][1]

    @property
    def priority_name(self):
        return IssuePriority[self.priority-1][1]

    @property
    def slug(self):
        return '#%s-%d' % (self.project.slug.upper(), self.id)

    @property
    def submitted(self):
        return self.comment_set.all()[0].date


    @property
    def url(self):
        return reverse('bug-show', args=[self.project.slug, self.id])
    
    def __unicode__(self):
        return self.slug

    def fromSlug(slug):
        parts = slug[1:].split('-')
        if len(parts) <> 2:
            raise ValueError('Bad slug')
        else:
            return Bug.objects.get(project__slug__iexact=parts[0], id=int(parts[1]))

class Comment(models.Model):
    bug        = models.ForeignKey(Bug)
    submitter  = models.ForeignKey(User)
    date       = models.DateTimeField(auto_now_add=True)
    text       = models.TextField()

def up_file(this, name):
    return 'bugfiles/%d-%d/%s' % (this.bug_id, this.comment_id, name)

class Attachment(models.Model):
    bug        = models.ForeignKey(Bug)
    comment    = models.ForeignKey(Comment)
    file       = models.FileField(upload_to = up_file, verbose_name='Attachment')
    @property
    def file_name(self):
        return os.path.basename(str(self.file))

    @property
    def url(self):
        return reverse('bug-attachment', args=[self.bug.project.slug, self.id])

def autojoin(l):
    s = unicode(l[0])
    rem = l[1:]
    for o in rem:
        s += ', ' + unicode(o)
    return s

class Action(models.Model):
    bug       = models.ForeignKey(Bug)
    comment   = models.ForeignKey(Comment)
    field     = models.TextField(max_length=32)
    value     = models.TextField(max_length=32)

    @classmethod
    def for_change(self, bug, comment, field, oldv, newv):
        changed = False
        valstr  = str(newv)
        if field == 'depends' or field =='blocks':
            soldv = set(oldv.all())
            snewv = set(newv)
            changed = len(soldv ^ snewv)
            if len(newv):
                valstr = autojoin(newv)
            else:
                valstr = 'none'
        elif isinstance(newv, models.Model):
            oldv = oldv.pk
            newv = newv.pk
            changed = oldv <> newv
        else:
            changed = oldv <> newv

        if changed:
            a = Action(bug=bug, comment=comment, field=field, value=valstr)
            a.save()
            return a

    def __unicode__(self):
        try:
            name  = getattr(Bug, self.field).verbose_name
        except AttributeError:
            name = self.field[0].upper() + self.field[1:]
        curval = getattr(self.bug, self.field)
        val    = self.value
        if isinstance(curval, models.Model):
            try:
                val = curval.__class__.objects.get(pk=val)
            except:
                pass
        return "Changed %s to %s" % (name, val)

