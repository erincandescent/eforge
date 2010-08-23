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
    __slots__ = ('ex', 'obj')

    def __init__(self, ex, obj):
        self.ex  = ex
        self.obj = obj

    @property
    def ready(self):
        return True

    def value(self):
        if self.ex:
            raise self.ex
        else:
            return self.obj

class Task(object):
    def __init__(self, fn, **kwargs):
        self.fn          = fn

    def bind(self, **kwargs):
        return self

    def __call__(self, *args, **kwargs):
        try:
            return Future(None, self.fn(*args, **kwargs))
        except Exception, e:
            return Future(e, None)

        return Future(ex, None)

def task(**kwargs):
    def builder(fn):
        return Task(fn, **kwargs)
    return builder