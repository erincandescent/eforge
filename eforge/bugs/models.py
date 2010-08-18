# -*- coding: utf-8 -*-
from django.db import models
from eforge.models import Project, Milestone
from eforge.utils.picklefield import PickledObjectField
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

IssueStatus = (
    (1, 'New'),
    (2, 'Assigned'),
    (3, 'Reopened'),
    (4, 'In Progress'),
    (5, 'Resolved'),
)

IssueResolution = (
    (1, 'Fixed'),
    (2, 'Invalid'),
    (3, 'Won\'t Fix'),
    (4, 'Duplicate'),
    (5, 'Works for me'),
    (6, 'Incomplete'),
)
class Bug(models.Model):
    project    = models.ForeignKey(Project)
    component  = models.ForeignKey(Component)
    priority   = models.SmallIntegerField(choices=IssuePriority, default=4)
    issue_type = models.SmallIntegerField(choices=IssueType, default=1)
    title      = models.CharField(max_length=50)

    target     = models.ForeignKey(Milestone)

    status     = models.SmallIntegerField(choices=IssueStatus, default=1)
    resolution = models.SmallIntegerField(choices=IssueResolution, default=0, blank=True)

    submitter  = models.ForeignKey(User, related_name='submitted_bugs')
    owner      = models.ForeignKey(User, related_name='owned_bugs', blank=True, null=True)

    depends    = models.ManyToManyField('self', symmetrical=False, related_name='blocks', blank=True)

    watchers   = models.ManyToManyField(User, related_name='watching_bugs', blank=True)

    @property
    def issue_type_name(self):
        return IssueType[self.issue_type-1][1]

    @property
    def priority_name(self):
        return IssuePriority[self.priority-1][1]

    @property
    def status_name(self):
        return IssueStatus[self.status-1][1]

    @property
    def resolution_name(self):
        return IssueResolution[self.resolution-1][1]

    @property
    def is_resolved(self):
        return self.status == 5

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

# Renderers for action fields:
def component_renderer(old, to):
    cold = Component.objects.get(pk=old)
    cto   = Component.objects.get(pk=to)
    return 'Changed Component from %s to %s' % (cold, cto)

def target_renderer(old, to):
    mold = Milestone.objects.get(pk=old)
    mto  = Milestone.objects.get(pk=to)
    return 'Changed Milestone from %s to %s' % (mold, mto)

def priority_renderer(old, to):
    pold = IssuePriority[old-1][1]
    pto   = IssuePriority[to-1][1]
    return 'Changed Priority from %s to %s' % (pold, pto)

def issue_type_renderer(old, to):
    told = IssueType[old-1][1]
    tto   = IssueType[to-1][1]
    return 'Changed Issue Type from %s to %s' % (told, tto)

def title_renderer(old, to):
    return 'Changed Title from "%s" to "%s"' % (old, to)

def status_renderer(old, to):
    sold = IssueStatus[old-1][1]
    sto   = IssueStatus[to-1][1]
    return 'Changed Issue Type from %s to %s' % (sold, sto)

def resolution_renderer(old, to):
    rto = IssueResolution[to-1][1]
    return 'Set resolution to %s' % rto

def owner_renderer(old, to):
    if old and to:
        oold = User.objects.get(pk=old)
        oto   = User.objects.get(pk=to)
        return 'Changed Owner from %s to %s' % (oold, oto)
    elif old:
        oold = User.objects.get(pk=old)
        return 'Removed assignment to %s' % oold
    else:
        oto   = User.objects.get(pk=to)
        return 'Assigned to %s' % oto

def autojoin(l, format):
    if len(l) == 0: return ''
    l = list(l)
    s = format(l[0])
    rem = l[1:]
    for o in rem:
        s += ', ' + format(o)
    return s

def get_dep(id):
    return Bug.objects.get(pk=id)

def depends_renderer(old, to):
    sold = set(old)
    sto   = set(to)

    removed = sold - sto
    added   = sto - sold

    tremoved = autojoin(removed, get_dep)
    tadded   = autojoin(added,   get_dep)

    if len(removed) == 0:
        return 'Added dependencies on %s' % tadded
    elif len(added) == 0:
        return 'Removed dependencies on %s' % tremoved
    else:
        return 'Removed dependencies on %s; added %s' % (tadded, tremoved)

action_renderer = {
    'component':        component_renderer,
    'priority':         priority_renderer,
    'issue_type':       issue_type_renderer,
    'title':            title_renderer,
    'status':           status_renderer,
    'resolution':       resolution_renderer,
    'owner':            owner_renderer,
    'depends':          depends_renderer,
    'target':           target_renderer,
}

class Action(models.Model):
    bug       = models.ForeignKey(Bug)
    comment   = models.ForeignKey(Comment)
    field     = models.TextField(max_length=32)
    value     = PickledObjectField()

    @classmethod
    def for_change(self, bug, comment, field, oldv, newv):
        changed = False
        valstr  = str(newv)
        if isinstance(oldv, models.Model): oldv = oldv.pk
        if isinstance(newv, models.Model): newv = newv.pk

        if field == 'depends' or field =='blocks':
            oldv = [o.pk for o in oldv.all()]
            newv = [o.pk for o in newv]
            changed = len(set(oldv) ^ set(newv))
            changed = oldv <> newv
        else:
            changed = oldv <> newv

        if changed:
            a = Action(bug=bug, comment=comment, field=field, value=(oldv, newv))
            a.save()
            return a

    def __unicode__(self):
        try:
            name  = getattr(Bug, self.field).verbose_name
        except AttributeError:
            name = self.field.title()
        curval = getattr(self.bug, self.field)
        val    = self.value

        if name == 'Issue_type':
            name = 'Issue Type'

        return action_renderer[self.field](val[0], val[1])

