# -*- coding: utf-8 -*-
import json

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required

from organizations.models import Organization
from threebot.models import Task, WorkflowTask, Workflow
from threebot.utils import get_my_orgs, create_workflow_with, has_admin_permission, clone_task_for_team
from threebot.forms import TaskChangeForm, TaskCreateForm, TaskImportForm


@login_required
def list(request, template='threebot/task/list.html'):
    orgs = get_my_orgs(request)
    tasks = Task.objects.filter(owner__in=orgs)

    return render(request, template, {'tasks': tasks})


@login_required
def task_permalink(request, id):
    orgs = get_my_orgs(request)
    task = get_object_or_404(Task, owner__in=orgs, id=id)
    return redirect('core_task_detail', slug=task.slug)


@login_required
def detail_edit(request, slug, template='threebot/task/detail_edit.html'):
    orgs = get_my_orgs(request)
    task = get_object_or_404(Task, owner__in=orgs, slug=slug, is_builtin=False)

    if task.is_builtin and not has_admin_permission(request.user, task.owner):
        raise Http404

    form = TaskChangeForm(request.POST or None, instance=task, )

    if form.is_valid():
        task = form.save()

        if '_continue' in form.data:
            # rerirect back to detailview
            return redirect('core_task_detail', slug=task.slug)
        elif '_addanother' in form.data:
            # redirect to create page
            return redirect('core_task_create')
        else:  # _save
            # redirect to listview
            return redirect('core_task_list')

    return render(request, template, {'task': task, 'form': form, 'affected_workflow_tasks': WorkflowTask.objects.filter(task=task)})


@login_required
def detail_digest(request, slug, template='threebot/task/detail_digest.html'):
    orgs = get_my_orgs(request)
    task = get_object_or_404(Task, owner__in=orgs, slug=slug, is_builtin=False)

    # get all workflows this task is used in
    workflows = Workflow.objects.filter(tasks__id=task.id)

    if task.is_builtin and not has_admin_permission(request.user, task.owner):
        raise Http404

    return render(request, template, {'task': task, 'workflows': workflows})


@login_required
def create(request, template='threebot/task/create.html', initial={}):
    form = TaskCreateForm(request.POST or None, request=request)
    if initial:
        form = TaskCreateForm(request.POST or None, initial=initial, request=request)

    if form.is_valid():
        task = form.save()

        if '_continue' in form.data:
            # rerirect back to detailview
            return redirect('core_task_detail', slug=task.slug)
        elif '_addanother' in form.data:
            # redirect to create page
            return redirect('core_task_create')
        else:  # _save
            # redirect to listview
            return redirect('core_task_list')

    return render(request, template, {'form': form})


@login_required
def import_task(request, template='threebot/task/import.html'):
    form = TaskImportForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        content = ""
        lines = request.FILES['task_json']
        for line in lines:
            content += line
        initial = json.loads(content)

        if '_import_and_save' in form.data:
            request.POST = initial
        else:  # _import
            request.POST = {}

        return create(request, initial=initial)

    return render(request, template, {'form': form})


@login_required
def export(request, slug):
    orgs = get_my_orgs(request)
    task = get_object_or_404(Task, owner__in=orgs, slug=slug, is_readonly=False, is_builtin=False)

    task_dict = {
        'title': task.title,
        'desc': task.desc,
        'template': task.template,
    }

    task_json = json.dumps(task_dict)
    response = HttpResponse(task_json, content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=%s' % task.slug
    return response


@login_required
def create_workflow(request, slug):
    orgs = get_my_orgs(request)
    task = get_object_or_404(Task, owner__in=orgs, slug=slug)

    workflow = create_workflow_with(task)
    return redirect('core_workflow_detail', slug=workflow.slug)


@login_required
def clone_for_team(request, taskslug, teamslug):
    orgs = get_my_orgs(request)
    task = get_object_or_404(Task, owner__in=orgs, slug=taskslug)
    team = Organization.objects.get(slug=teamslug)

    cloned_task = clone_task_for_team(request.user, task, team)

    if cloned_task.is_builtin or cloned_task.is_readonly:
        return redirect('core_task_list')

    return redirect('core_task_detail', slug=cloned_task.slug)


@login_required
def delete(request, slug, template='threebot/task/delete.html'):
    """Update a group.

    :param template: A custom template.
    """
    orgs = get_my_orgs(request)
    # TODO: this need more logic
    # dont delete builtin and readonly tasks by not admin users ..
    task = get_object_or_404(Task, owner__in=orgs, slug=slug)

    if request.method == 'POST':
        new_data = request.POST.copy()
        if new_data['sure_delete'] == 'Yes':
            task.delete()
            return redirect('core_task_list')
        else:
            return redirect('core_task_detail', slug=task.slug)

    return render(request, template, {'task': task, 'affected_workflow_tasks': WorkflowTask.objects.filter(task=task)})
