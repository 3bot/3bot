# -*- coding: utf-8 -*-
import json
try:
    from urllib.parse import unquote_plus
except ImportError:
    from urllib import unquote_plus

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from threebot.models import Task
from threebot.models import Worker
from threebot.models import Workflow
from threebot.models import WorkflowTask
from threebot.models import WorkflowPreset
from threebot.models import UserParameter, Parameter
from threebot.models import OrganizationParameter, ParameterList
from threebot.models import WorkflowLog
from threebot.tasks import run_workflow
from threebot.utils import order_workflow_tasks, render_templates, get_my_orgs, filter_workflow_log_history
from threebot.forms import TaskParameterForm, WorkflowReorderForm, WorkflowCreateForm, WorkflowChangeForm, WorkerSelectForm, UserParameterCreateForm, ParameterListSelectForm


@login_required
def list(request, template='threebot/workflow/list.html'):
    orgs = get_my_orgs(request)
    workflows = Workflow.objects.filter(owner__in=orgs)

    return render(request, template, {'workflows': workflows})


@login_required
def create(request, template='threebot/workflow/create.html'):
    form = WorkflowCreateForm(request.POST or None, request=request)

    if form.is_valid():
        workflow = form.save()

        if '_continue' in form.data:
            # rerirect to detailview
            return redirect('core_workflow_detail', slug=workflow.slug)
        elif '_addanother' in form.data:
            # redirect to create page
            return redirect('core_workflow_create')
        else:  # _save
            # redirect to reorder view
            return redirect('core_workflow_detail_reorder', slug=workflow.slug)

    return render(request, template, {'form': form})


@login_required
def workflow_permalink(request, id):
    workflow = get_object_or_404(Workflow, id=id)
    return redirect('core_workflow_detail', slug=workflow.slug)


@login_required
def detail_digest(request, slug, template='threebot/workflow/detail_digest.html'):
    orgs = get_my_orgs(request)
    workflow = get_object_or_404(Workflow, owner__in=orgs, slug=slug)
    logs = filter_workflow_log_history(workflow=workflow, quantity=20)

    return render(request, template, {'workflow': workflow, 'logs': logs})


@login_required
def detail_edit(request, slug, template='threebot/workflow/detail_edit.html'):
    orgs = get_my_orgs(request)
    workflow = get_object_or_404(Workflow, owner__in=orgs, slug=slug)

    form = WorkflowChangeForm(request.POST or None, instance=workflow, )

    if form.is_valid():
        workflow = form.save()

        if '_continue' in form.data:
            # rerirect back to detailview
            return redirect('core_workflow_detail_reorder', slug=workflow.slug)
        elif '_addanother' in form.data:
            # redirect to create page
            return redirect('core_workflow_create')
        else:  # _save
            # redirect to listview
            return redirect('core_workflow_list')

    return render(request, template, {'form': form, 'workflow': workflow})


@login_required
def detail_perf(request, slug, template='threebot/workflow/detail_perf.html'):
    orgs = get_my_orgs(request)
    workflow = get_object_or_404(Workflow, owner__in=orgs, slug=slug)

    wf_preset, created = WorkflowPreset.objects.get_or_create(user=request.user, workflow=workflow)
    preset = {}
    ready_to_perform = False  # if true: each form is valid an request method is POST

    logs = filter_workflow_log_history(workflow=workflow, quantity=5)

    workflow_tasks = order_workflow_tasks(workflow)

    # serve relevant forms
    initials_for_worker_form = {}
    if request.GET.get('worker'):
        initials_for_worker_form['worker'] = request.GET.get('worker')
    worker_form = WorkerSelectForm(request.POST or None, request=request, workflow=workflow, initial=initials_for_worker_form)
    for wf_task in workflow_tasks:
        extra = wf_task.task.required_inputs
        wf_task.form = TaskParameterForm(request.POST or None, request=request, extra=extra, workflow_task=wf_task)

    if request.method == 'POST':
        ready_to_perform = True

        if worker_form.is_valid():
            worker_ids = worker_form.cleaned_data['worker']
            preset.update({'worker_id': worker_ids})
        else:
            ready_to_perform = False

        for wf_task in workflow_tasks:
            if wf_task.form.is_valid():
                pass
            else:
                ready_to_perform = False

    if ready_to_perform:
        inp = {}

        for wf_task in workflow_tasks:
            data = wf_task.form.cleaned_data
            preset.update({wf_task.id: {}})

            form_dict = {}
            for data_type in Parameter.DATA_TYPE_CHOICES:
                form_dict[data_type[0]] = {}

            for template_input, path_to_value in data.iteritems():  # TODO: better identifier
                # template_input = "wt_task_1.email.recipient_email"
                # path_to_value = "prompt.email.name@provider.com"
                # path_to_value = "output.string.output_<WorkflowTask.id>"

                template_input_list = template_input.split('.')
                wf_task_id = template_input_list[0]
                template_input_data_type = template_input_list[1]
                template_input_name = template_input_list[2]

                path_to_value_list = path_to_value.split('.')
                param_owner = path_to_value_list[0]
                if len(path_to_value_list) == 3:
                    param_data_type = path_to_value_list[1]
                    param_name = path_to_value_list[2]

                # k[0] = wt_task id:
                # k[1] = data_type:
                # k[2] = value:

                # val[0] = param owner
                # val[1] = param data_type
                # val[2] = param name

                if param_owner == 'global':
                    value = OrganizationParameter.objects.get(data_type=param_data_type, name=param_name)
                    form_dict[template_input_data_type][template_input_name] = value.value
                if param_owner == 'user':
                    value = UserParameter.objects.get(data_type=param_data_type, name=param_name, owner=request.user)
                    form_dict[template_input_data_type][template_input_name] = value.value
                if param_owner == 'output':
                    # we set this to "output_<id>". while performing we replace this with the output returned from the WorkflowTask with id = <id>
                    form_dict[template_input_data_type][template_input_name] = '%s' % str(param_name)
                if param_owner == 'prompted':
                    prompted_value = data['prompt_%s' % template_input].split('.', 2)
                    form_dict[template_input_data_type][template_input_name] = prompted_value[2]

                # update presets
                if not wf_task.form[template_input].is_hidden:
                    templatefield = '%s.%s' % (template_input_data_type, template_input_name)

                    preset[wf_task.id][templatefield] = path_to_value

            inp['%s' % wf_task.id] = form_dict

            wf_preset.defaults = preset
            wf_preset.save()

        workers = Worker.objects.filter(id__in=worker_ids)

        for worker in workers:
            workflow_log = WorkflowLog(workflow=workflow, inputs=inp, outputs={}, performed_by=request.user, performed_on=worker)
            workflow_log.save()

            run_workflow(workflow_log.id)

        return redirect('core_workflow_log_detail', slug=workflow.slug, id=workflow_log.id)  # redirects to latest

    # else:
    #     raise("error")

    return render(request, template, {'workflow': workflow, 'workflow_tasks': workflow_tasks, 'worker_form': worker_form, 'logs': logs, 'parameter_form': UserParameterCreateForm(user=request.user)})


@login_required
def detail_perf_with_list(request, slug, template='threebot/workflow/detail_perf_with_list.html'):
    orgs = get_my_orgs(request)
    workflow = get_object_or_404(Workflow, owner__in=orgs, slug=slug)

    initials_for_worker_form = {}
    if request.GET.get('worker'):
        initials_for_worker_form['worker'] = request.GET.get('worker')
    worker_form = WorkerSelectForm(request.POST or None, request=request, workflow=workflow, initial=initials_for_worker_form)

    initials_for_list_form = {}
    if request.GET.get('list'):
        initials_for_list_form['parameter_list'] = request.GET.get('list')
    list_form = ParameterListSelectForm(request.POST or None, request=request, workflow=workflow, initial=initials_for_list_form)
    workflow_tasks = order_workflow_tasks(workflow)

    if worker_form.is_valid() and list_form.is_valid():
        worker_ids = worker_form.cleaned_data['worker']
        workers = Worker.objects.filter(id__in=worker_ids)

        list_id = list_form.cleaned_data['parameter_list']
        parameter_list = ParameterList.objects.get(id=list_id)
        input_dict = {}

        for wf_task in workflow_tasks:
            l_input_dict = {}
            for data_type in Parameter.DATA_TYPE_CHOICES:
                l_input_dict[data_type[0]] = {}

            for parameter in parameter_list.parameters.all():
                l_input_dict[parameter.data_type][parameter.name] = parameter.value

            input_dict['%s' % wf_task.id] = l_input_dict

        for worker in workers:
            workflow_log = WorkflowLog(workflow=workflow, inputs=input_dict, outputs={}, performed_by=request.user, performed_on=worker)
            workflow_log.save()

            wf_preset, created = WorkflowPreset.objects.get_or_create(user=request.user, workflow=workflow)
            wf_preset.defaults.update({'worker_id': worker_ids})
            wf_preset.defaults.update({'list_id': parameter_list.id})
            wf_preset.save()

            run_workflow(workflow_log.id)

        return redirect('core_workflow_log_detail', slug=workflow.slug, id=workflow_log.id)

    logs = filter_workflow_log_history(workflow=workflow, quantity=5)

    return render(request, template, {'workflow': workflow, 'workflow_tasks': workflow_tasks, 'worker_form': worker_form, 'list_form': list_form, 'logs': logs})


@login_required
def delete(request, slug, template='threebot/workflow/delete.html'):
    """
    """
    orgs = get_my_orgs(request)
    workflow = get_object_or_404(Workflow, owner__in=orgs, slug=slug)

    if request.method == 'POST':
        new_data = request.POST.copy()
        if new_data['sure_delete'] == 'Yes':
            workflow.delete()
            return redirect('core_workflow_list')
        else:
            return redirect('core_workflow_detail_edit', slug=workflow.slug)

    return render(request, template, {'workflow': workflow})


@login_required
def detail_reorder(request, slug, template='threebot/workflow/detail_reorder.html'):
    workflow = Workflow.objects.get(slug=slug)
    tasks = Task.objects.filter(owner=workflow.owner)
    workflow_tasks = order_workflow_tasks(workflow)

    form = WorkflowReorderForm(request.POST or None)

    if form.is_valid():
        decoded = json.loads(form.cleaned_data['order'])

        # delete all wf_tasks for workflow and create new from form data
        for workflow_task in workflow_tasks:
            workflow_task.delete()

        prev = None
        for idx, order_item in enumerate(decoded[0]):
            curr_task = Task.objects.get(id=order_item['id'])
            curr = WorkflowTask(task=curr_task, workflow=workflow)
            curr.save()

            if prev:
                curr.prev_workflow_task = prev
                curr.save()
                prev.next_workflow_task = curr
                prev.save()
            prev = curr

        # redirect back to detail view
        return redirect('core_workflow_detail', workflow.slug)

    return render(request, template, {'workflow': workflow, 'workflow_tasks': workflow_tasks, 'tasks': tasks, 'form': form})


@login_required
def log_detail(request, slug, id, template='threebot/workflow/log.html'):
    orgs = get_my_orgs(request)
    workflow_log = get_object_or_404(WorkflowLog, id=id)
    workflow = get_object_or_404(Workflow, owner__in=orgs, slug=slug)
    try:
        templates = render_templates(workflow_log, mask=True)
    except Exception as e:
        templates = None

    try:
        outputs = sorted(workflow_log.outputs.iteritems())
    except AttributeError:
        outputs = None

    return render(request, template, {'workflow': workflow, 'workflow_log': workflow_log, 'outputs': outputs, 'templates': templates})


@login_required
def log_detail_render(request, slug, id):
    # get id params, slug+type
    format = request.GET.get("format", 'raw')
    wf_task_slug = request.GET.get("task")

    orgs = get_my_orgs(request)
    workflow_log = get_object_or_404(WorkflowLog, id=id)
    workflow = get_object_or_404(Workflow, owner__in=orgs, slug=slug)
    lookup_key = unquote_plus(wf_task_slug)
    output_item = workflow_log.outputs[lookup_key]

    try:
        output = output_item['stdout']
    except KeyError:
        output = output_item['output']

    if format == 'raw':
        return HttpResponse(output, content_type="text/plain")
    elif format == 'html':
        return HttpResponse(output, content_type="text/html")


@login_required
def replay(request, slug, id):
    orgs = get_my_orgs(request)
    workflow = get_object_or_404(Workflow, owner__in=orgs, slug=slug)

    old_log = get_object_or_404(WorkflowLog, id=id)
    new_log = WorkflowLog(workflow=workflow, inputs=old_log.inputs, outputs={}, performed_by=request.user, performed_on=old_log.performed_on)
    new_log.save()

    run_workflow(new_log.id)
    return redirect('core_workflow_log_detail', slug=slug, id=new_log.id)


@login_required
def workflow_log_permalink(request, id):
    """
    Acts like a proxy that redirects a WorkflowLog.id to 'core_workflow_log_detail'
    """
    workflow_log = get_object_or_404(WorkflowLog, id=id)
    return redirect('core_workflow_log_detail', slug=workflow_log.workflow.slug, id=workflow_log.id)
