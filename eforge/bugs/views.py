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
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.views.generic.list_detail import object_list
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django import forms
from eforge.decorators import project_page
from eforge.models import Project, Milestone
from models import *

class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        exclude   = ('watchers', 'project', 'submitter')
        protected = ('title', 'priority', 'issue_type', 'owner', 'depends', 'component',
                     'status', 'resolution')

    def __init__(self, *args, **kwargs):
        super(BugForm, self).__init__(*args, **kwargs)
        self.fields['component'].queryset = Component.objects.filter(project=self.instance.project)
        self.fields['target'].queryset = Milestone.objects.filter(project=self.instance.project)

    def clean(self):
        try:
            int(self.cleaned_data['resolution'])
        except Exception, e:
            self.cleaned_data['resolution'] = 0

        return super(BugForm, self).clean()

    def protect_clean(self, after):
        for field in self.Meta.protected:
            self.cleaned_data[field] = getattr(self.instance, field)
        return after()

    def protect(self, user):
        if not user.has_perm('bugs.change_bug'):
            for field in self.Meta.protected:
                self.fields[field].widget = forms.HiddenInput()
            clean = self.clean
            self.clean = lambda: self.protect_clean(clean)

    def save_actions(self, comment):
        bugobj = Bug.objects.get(pk=self.instance.pk)
        for k in self.fields:
            newv = self.cleaned_data[k]
            oldv = getattr(bugobj, k)
            Action.for_change(self.instance, comment, k, oldv, newv)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('bug', 'submitter', 'date')

AttachmentFormSet = forms.models.modelformset_factory(Attachment, extra=3, exclude=('bug', 'comment', 'file_name'))

@project_page
def showbug(request, project, bug_id):
    bug     = get_object_or_404(Bug, project=project, id=bug_id)
    user    = request.user
    if user.is_active:
        comment = Comment(bug=bug, submitter=user)
    else: comment = None
    edit_form = False

    if request.method == 'POST':
        bug_form     = BugForm(request.POST, instance=bug, prefix='bug')
        comment_form = CommentForm(request.POST, instance=comment, prefix='comment')
        attach_forms = AttachmentFormSet(request.POST, request.FILES, prefix='attach', queryset=Attachment.objects.none())
        bug_form.protect(user)

        if bug_form.is_valid() and comment_form.is_valid() and attach_forms.is_valid() and user.is_authenticated:
            comment = comment_form.save()
            bug_form.save_actions(comment)
            bug_form.save()
            attachments = attach_forms.save(commit=False)
            for attachment in attachments:
                attachment.bug = bug
                attachment.comment = comment
                attachment.save()
            messages.info(request, 'Bug successfully updated')
            return redirect(reverse('bug-show', args = [project.slug, bug_id]))
        edit_form = True
    else:
        bug_form     = BugForm(instance=bug, prefix='bug')
        comment_form = CommentForm(instance=comment, prefix='comment')
        attach_forms = AttachmentFormSet(prefix='attach', queryset=Attachment.objects.none())
        bug_form.protect(user)

    return render_to_response('bugs/showbug.html', {
        'project':      project,
        'bug':          bug,
        'bug_form':     bug_form,
        'comment_form': comment_form,
        'attach_forms': attach_forms,
        'edit_form':    edit_form,
    }, context_instance=RequestContext(request))

@login_required
@project_page
def newbug(request, project):
    user    = request.user
    bug     = Bug(project=project, submitter=user)
    comment = Comment(bug=bug, submitter=user)

    if request.method == 'POST':
        bug_form     = BugForm(request.POST, instance=bug, prefix='bug')
        comment_form = CommentForm(request.POST, instance=comment, prefix='comment')
        attach_forms = AttachmentFormSet(request.POST, request.FILES, prefix='attach', queryset=Attachment.objects.none())

        if bug_form.is_valid() and comment_form.is_valid() and attach_forms.is_valid():
            bug = bug_form.save()
            comment = comment_form.save(commit=False)
            comment.bug = bug
            comment.save()
            attachments = attach_forms.save(commit=False)
            for attachment in attachments:
                attachment.bug = bug
                attachment.comment = comment
                attachment.save()
            user.message_set.create(message='Bug created')
            return redirect(reverse('bug-show', args = [project.slug, bug.id]))
    else:
        bug_form     = BugForm(prefix='bug', instance=bug)
        comment_form = CommentForm(prefix='comment', instance=comment)
        attach_forms = AttachmentFormSet(prefix='attach', queryset=Attachment.objects.none())

    return render_to_response('bugs/newbug.html', {
        'project':      project,
        'bug_form':     bug_form,
        'comment_form': comment_form,
        'attach_forms': attach_forms,
    }, context_instance=RequestContext(request))

class SearchForm(forms.Form):
    def __init__(self, proj, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.project = proj
        self.fields['component'].queryset=Component.objects.filter(project=self.project)
        self.fields['milestone'].queryset=Milestone.objects.filter(project=self.project)

    def clean(self):
        for f in self.fields:
            if len(self.cleaned_data[f]) == 0:
                if f == 'status':
                    self.cleaned_data[f] = [1, 2, 3, 4]
                else:
                    self.cleaned_data[f] = [x[0] for x in self.fields[f].choices]
        return super(SearchForm, self).clean()

    issue_type = forms.MultipleChoiceField(choices=IssueType, required=False)
    priority   = forms.MultipleChoiceField(choices=IssuePriority, required=False)
    status     = forms.MultipleChoiceField(choices=IssueStatus, required=False)
    component  = forms.ModelMultipleChoiceField(queryset=Component.objects, required=False)
    milestone  = forms.ModelMultipleChoiceField(queryset=Milestone.objects, required=False)

@project_page
def listbugs(request, project):
    search_form = SearchForm(project, request.GET)
    if search_form.is_valid():
        query = project.bug_set.filter(
            issue_type__in=search_form.cleaned_data['issue_type'],
              priority__in=search_form.cleaned_data['priority'],
                status__in=search_form.cleaned_data['status'],
             component__in=search_form.cleaned_data['component'],
                target__in=search_form.cleaned_data['milestone'],
        ).all()
    else:
        query = project.bug_set.all()

    page_size = 50 if 'num' not in request.GET else request.GET['num']
    page = 1 if 'page' not in request.GET else request.GET['page']

    return object_list(
        request,
        queryset=query,
        template_name='bugs/buglist.html',
        paginate_by=page_size,
        page=page,
        extra_context={
            'project': project,
            'search':  search_form,
        }
    )

@project_page
def attachment(request, project, attach_id):
    attachment = get_object_or_404(Attachment, bug__project=project, id=attach_id)
    path = attachment.file.path
    resp = HttpResponse(
        open(path, 'r'),
        content_type='text/plain'
    )
    resp['Content-Disposition'] = 'attachment; filename=%s' % attachment.file_name
    return resp
