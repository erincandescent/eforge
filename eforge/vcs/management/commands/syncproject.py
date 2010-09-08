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

from django.core.management.base import BaseCommand, CommandError
from eforge.models import Project
from eforge.vcs.sync import sync_project

class Command(BaseCommand):
    args = '<project_slug project_slug ...>'
    help = 'Synchronizes the specified project repositories with the database'

    def handle(self, *args, **options):
        for proj_slug in args:
            try:
                project = Project.objects.get(slug=proj_slug)
            except Project.DoesNotExist:
                raise CommandError('Project "%s" does not exist' % proj_slug)

            sync_project(project)