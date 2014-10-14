from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from ..models import Worker
from ..forms import WorkerChangeForm, WorkerCreateForm
from ..utils import get_my_orgs, filter_workflow_log_history


@login_required
def list(request, template='threebot/worker/list.html'):
    orgs = get_my_orgs(request)
    workers = Worker.objects.all().filter(owner__in=orgs)

    return render_to_response(template, {'request': request,
                                         'workers': workers,
                                        }, context_instance=RequestContext(request))


@login_required
def detail(request, slug, template='threebot/worker/detail.html'):
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

    return render_to_response(template, {'request': request,
                                         'worker': worker,
                                         'logs': logs,
                                         'form': form,
                                        }, context_instance=RequestContext(request))


@login_required
def create(request, template='threebot/worker/create.html'):
    form = WorkerCreateForm(request.POST or None, request=request)

    if form.is_valid():
        worker = form.save()

        return redirect('core_worker_manual', slug=worker.slug)

    return render_to_response(template, {'request': request,
                                         'form': form,
                                        }, context_instance=RequestContext(request))


@login_required
def manual(request, slug, template='threebot/worker/manual.html'):
    orgs = get_my_orgs(request)
    worker = get_object_or_404(Worker, owner__in=orgs, slug=slug)

    return render_to_response(template, {'request': request,
                                         'worker': worker,
                                        }, context_instance=RequestContext(request))


@login_required
def delete(request, slug, template='threebot/worker/delete.html'):
    """Update a group.

    :param template: A custom template.
    """
    orgs = get_my_orgs(request)
    worker = get_object_or_404(Worker, owner__in=orgs, slug=slug)

    if request.method == 'POST':
        new_data = request.POST.copy()
        if new_data['delete_group'] == 'Yes':
            worker.delete()
            return redirect('core_worker_list')
        else:
            return redirect('core_worker_detail', slug=worker.slug)

    return render_to_response(template, {'worker': worker,
                                        }, context_instance=RequestContext(request))
