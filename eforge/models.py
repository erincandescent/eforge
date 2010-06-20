from django.db import models

# Create your models here.
class Project(models.Model):
    slug        = models.SlugField(max_length=16, unique=True)
    name        = models.CharField(max_length=32, unique=True)
    repo_path   = models.CharField(max_length=64)
    description = models.TextField()

    def __unicode__(self):
        return self.name
