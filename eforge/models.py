# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import models
import plugins
from operator import itemgetter

def logo_path(proj, name):
    return 'projects/%s_%s' % (proj.slug, name)

# Create your models here.
class Project(models.Model):
    slug        = models.SlugField(max_length=16, unique=True)
    name        = models.CharField(max_length=32, unique=True)
    repo_path   = models.CharField(max_length=64)
    description = models.TextField()
    logo        = models.ImageField(upload_to=logo_path)
    members     = models.ManyToManyField(User)

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

class Milestone(models.Model):
    project     = models.ForeignKey(Project)
    previous    = models.OneToOneField('Milestone', related_name='next', blank=True, null=True)
    name        = models.CharField(max_length=32)
    description = models.TextField()
    due_date    = models.DateTimeField()
    completed   = models.BooleanField()

    def __unicode__(self):
        return self.name