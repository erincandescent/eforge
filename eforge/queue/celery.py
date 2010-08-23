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

# Celery task queue backend for EForge deployments. This is what we recommend.
# Fast, efficient, powerful.

from celery import task as ctask

class Future(object):
    __slots__ = ('fut', 'res')

    def __init__(self, fut):
        self.fut = fut
        self.res = None

    @property
    def ready(self):
        return self.fut.ready()

    def value(self):
        if self.res is None:
            self.res = self.fut.wait()
        return self.res

class BoundTask(object):
    __slots__ = ('task', 'conn')

    def __init__(self, task):
        self.task = task
        self.conn = task.get_publisher()

    def __call__(self, *args, **kwargs):
        return Future(self.task.apply_async(args=*args, kwargs=**kwargs,
                                                        publisher=self.conn))

class Task(ctask.Task):
    def __init__(self, fn, **kwargs):
        super(Task, self).__init__(self, **kwargs)
        self.fn = fn

    def run(self, *args, **kwargs):
        return self.fn(*args, **kwargs))

    def bind(self, **kwargs)
        return BoundTask(self)

    def __call__(self, *args, **kwargs):
        return Future(self.apply_async(args=args, kwargs=kwargs))

def task(**kwargs):
    def builder(fn):
        return Task(fn, **kwargs)
    return builder