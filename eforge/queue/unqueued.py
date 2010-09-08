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

# Unqueued queue backend for EForge deployments. This executes all actions
# synchronously; it is not a suitable backend for production deployments.

class Future(object):
    __slots__ = ('ex', 'obj', 'retrieved')

    def __init__(self, ex, obj):
        self.ex  = ex
        self.obj = obj
        self.retrieved = False

    @property
    def ready(self):
        return True

    def value(self):
        self.retrieved = True
        if self.ex:
            raise self.ex
        else:
            return self.obj
            
    def __del__(self):
        if not self.retrieved and self.ex:
            print "Future with exception: %s" % self.ex

class Task(object):
    def __init__(self, fn, **kwargs):
        self.fn          = fn

    def bind(self, **kwargs):
        return self

    def __call__(self, *args, **kwargs):
        print "Invoke task"
        try:
            return Future(None, self.fn(*args, **kwargs))
        except Exception, e:
            return Future(e, None)

        return Future(ex, None)

def task(**kwargs):
    def builder(fn):
        print "Build fn"
        return Task(fn, **kwargs)
    return builder