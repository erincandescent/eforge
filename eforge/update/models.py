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
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from eforge.models import Project
from datetime import datetime

class Update(models.Model):
    """
        The update is a generic class representing all project activities.
        It connects to a model which contains the actual activity data;
        the update object itself contains just the bare minimum information
        required to efficiently display and distribute the updates.
        
        In order to create a new update type, you must create a child class of 
        your model called Update. To this, you must add methods in the form
            def summary(model_object):
                pass
                
        These methods will be invoked when a user queries an instance of the update for your model. You should then construct an Update object with values appropriate to the update being created.
        
        The update will be pushed out to any listeners when you save the object.
        
        .. py:attribute:: user
            The user responsible for the update
            
        .. py:attribute:: project
            The project the update is connected to
            
        .. py:attribute:: date
            The date and time at which the update was created
            (Will be set to the time when the update object was created by
            default; you can override this by providing a date function)
            
        .. py:attribute:: object
            The object containing the main data on the update. This is a content
            types generic relation; it is a composite of (object_type, object_id)
            
        .. py:attribute:: summary
            A short summary of the update, usable for titles and short 
            notifications (e.g. tweets) [proxied]
            
        .. py:attribute:: description
            A more elaborate description of the update, for example, to be used as the body of E-Mail notifications [proxied]
            
        .. py:attribute:: url
            A link which the user can visit to gather more information [proxied]
            
        .. py:attribute:: recipients
            List of users who have expressed interest in direct notification of an update. This is optional; if not specified, none will be assumed
            [proxied]
    """

    user        = models.ForeignKey(User, null=True)
    project     = models.ForeignKey(Project, null=True)
    date       = models.DateTimeField(auto_now_add=True)

    object_type = models.ForeignKey(ContentType)
    object_id   = models.PositiveIntegerField()
    object      = generic.GenericForeignKey('object_type', 'object_id')
    
def _on_update(sender, instance, created, **kwargs):
    if not created:
        return
        
    make_update(instance)
    
def _on_delete(sender, instance, **kwargs):
    instance.update.delete()
    
def make_update(instance):
    """
        Makes a new update, based upon :instance:.
    """
    def _now(instance):
        return datetime.utcnow()
        
    upd = Update(user    = instance.Update.user(instance),
                 project = instance.Update.project(instance),
                 date    = getattr(instance.Update, 'date', _now)(instance),
                 object  = instance
    )
    upd.save()
    
def register_update_type(model):
    """
        Registers a model as being an update type. Whenever an instance of this
        model is saved, a new Update will automatically be created.
        
        In order to fill in the user and group properties, you must provide user and group methods (taking an instance of your model) in your Update 
        class.
        
        The :update: property will be added to your mode, through which you can find the instance corresponding to a model.
    """
    
    model.update = generic.GenericRelation(Update)
    
    post_save.connect(_on_update, sender=model)
    pre_delete.connect(_on_delete, sender=model)
    
def _proxy_property(name, default=None):
    def required_property(self):
        raise TypeError('Update object %s lacks property %s' % (self, name))

    default = default or required_property

    def the_property(self):
        model = ContentType.objects.get_for_model(self.object_type)
        return getattr(model.Update, name, default)(self.object)

    setattr(Update, name, property(the_property))
    
_proxy_property('summary')
_proxy_property('description')
_proxy_property('url')
_proxy_property('recipients', lambda o: [])