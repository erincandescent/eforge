from django.db import models
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.views.generic.list_detail import object_list
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django import forms
from e43.eforge.models import Project
from models import Component, Bug, Comment, Attachment, Action

class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        exclude   = ('watchers', 'project', 'submitter')
        protected = ('title', 'priority', 'issue_type', 'owner', 'depends', 'component')

    def __init__(self, *args, **kwargs):
        super(BugForm, self).__init__(*args, **kwargs)
        self.fields['component'].queryset = Component.objects.filter(project=self.instance.project)

    def protect_clean(self, after):
        for field in self.Meta.protected:
            self.cleaned_data[field] = getattr(self.instance, field)

    def protect(self, user):
        if not user.has_perm('bugs.change_bug'):
            for field in self.Meta.protected:
                self.fields[field].widget = forms.HiddenInput()
            self.clean = lambda: self.protect_clean(self.clean)

    def save_actions(self, comment):
        for k in self.fields:
            newv = self.cleaned_data[k]
            oldv = getattr(self.instance, k)
            Action.for_change(self.instance, comment, k, oldv, newv)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('bug', 'submitter', 'date')

AttachmentFormSet = forms.models.modelformset_factory(Attachment, extra=3, exclude=('bug', 'comment', 'file_name'))

def showbug(request, proj_slug, bug_id):
    project = get_object_or_404(Project, slug=proj_slug)
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
            user.message_set.create(message='Bug successfully updated')
            return redirect(reverse('bug-show', args = [proj_slug, bug_id]))
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
    }, context_instance=RequestContext(request))

@login_required
def newbug(request, proj_slug):
    project = get_object_or_404(Project, slug=proj_slug)
    user    = request.user
    bug     = Bug(project=project, submitter=user)
    comment = Comment(bug=bug, submitter=user)

    if request.method == 'POST':
        bug_form     = BugForm(request.POST, instance=bug)
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
            return redirect(reverse('bug-show', args = [proj_slug, bug.id]))
    else:
        bug_form     = BugForm(prefix='bug', instance=bug)
        comment_form = CommentForm(prefix='comment', instance=comment)
        attach_forms = AttachmentFormSet(prefix='attach', queryset=Attachment.objects.none())

    bug_form.as_table()
    comment_form.as_table()
    attach_forms.as_table()
    return render_to_response('bugs/newbug.html', {
        'project':      project,
        'bug_form':     bug_form,
        'comment_form': comment_form,
        'attach_forms': attach_forms,
    }, context_instance=RequestContext(request))

def listbugs(request, proj_slug):
    project = get_object_or_404(Project, slug=proj_slug)
    query=project.bug_set.all()

    page_size = 50 if 'num' not in request.GET else request.GET['num']
    page = 1 if 'page' not in request.GET else request.GET['page']

    return object_list(
        request,
        queryset=query,
        template_name='bugs/buglist.html',
        paginate_by=page_size,
        page=page,
        extra_context={'project': project}
    )

def attachment(request, proj_slug, attach_id):
    attachment = get_object_or_404(Attachment, bug__project__slug__iexact=proj_slug, id=attach_id)
    path = attachment.file.path
    resp = HttpResponse(
        open(path, 'r'),
        content_type='text/plain'
    )
    resp['Content-Disposition'] = 'attachment; filename=%s' % attachment.file_name
    return resp
