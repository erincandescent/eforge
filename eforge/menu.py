# -*- coding: utf-8 -*-
class ItemOrder(object):
    __slots__ = ['order', 'str']

    def __init__(self, order, str):
        self.order = order
        self.str = str

    def __cmp__(self, other):
        return self.order - other.order
        
    def __unicode__(self):
        return self.str
        
    def __str__(self):
        return self.str