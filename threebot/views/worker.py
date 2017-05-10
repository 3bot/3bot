# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from threebot.models import Worker
from threebot.forms import WorkerChangeForm, WorkerCreateForm
from threebot.utils import get_my_orgs, filter_workflow_log_history


@login_required
def list(request, template='threebot/worker/list.html'):
    orgs = get_my_orgs(request)
    workers = Worker.objects.all().filter(owner__in=orgs)

    return render(request, template, {'workers': workers})


@login_required
def worker_permalink(request, id):
    orgs = get_my_orgs(request)
    worker = get_object_or_404(Worker, owner__in=orgs, id=id)
    return redirect('core_worker_detail', slug=worker.slug)


@login_required
def detail_edit(request, slug, template='threebot/worker/detail_edit.html'):
    orgs = get_my_orgs(request)
    worker = get_object_or_404(Worker, owner__in=orgs, slug=slug)

    form = WorkerChangeForm(request.POST or None, instance=worker, )

    if form.is_valid():
        worker = form.save()

        if '_continue' in form.data:
            # rerirect back to detailview
            return redirect('core_worker_detail', slug=worker.slug)
        elif '_addanother' in form.data:
            # redirect to create page
            return redirect('core_worker_create')
        else:  # _save
            # redirect to listview
            return redirect('core_worker_list')

    logs = filter_workflow_log_history(worker=worker, quantity=5)

    return render(request, template, {'worker': worker, 'logs': logs, 'form': form})


@login_required
def detail_manual(request, slug, template='threebot/worker/detail_manual.html'):
    orgs = get_my_orgs(request)
    worker = get_object_or_404(Worker, owner__in=orgs, slug=slug)

    return render(request, template, {'worker': worker})


@login_required
def detail_digest(request, slug, template='threebot/worker/detail_digest.html'):
    orgs = get_my_orgs(request)
    worker = get_object_or_404(Worker, owner__in=orgs, slug=slug)
    logs = filter_workflow_log_history(worker=worker, quantity=20)

    return render(request, template, {'worker': worker, 'logs': logs})


@login_required
def create(request, template='threebot/worker/create.html'):
    form = WorkerCreateForm(request.POST or None, request=request)

    if form.is_valid():
        worker = form.save()

        return redirect('core_worker_detail_manual', slug=worker.slug)

    return render(request, template, {'form': form})


@login_required
def delete(request, slug, template='threebot/worker/delete.html'):
    """Update a group.

    :param template: A custom template.
    """
    orgs = get_my_orgs(request)
    worker = get_object_or_404(Worker, owner__in=orgs, slug=slug)

    if request.method == 'POST':
        new_data = request.POST.copy()
        if new_data['sure_delete'] == 'Yes':
            worker.delete()
            return redirect('core_worker_list')
        else:
            return redirect('core_worker_detail', slug=worker.slug)

    return render(request, template, {'worker': worker})
