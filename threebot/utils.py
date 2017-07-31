from django.contrib.auth.decorators import login_required
from django.template import Template, Context

from organizations.models import Organization, OrganizationUser, OrganizationOwner

from threebot.models import UserParameter
from threebot.models import OrganizationParameter
from threebot.models import WorkflowPreset, WorkflowTask, Worker, Workflow, Task, WorkflowLog, ParameterList

import logging

logger = logging.getLogger('3bot')


def filter_workflow_log_history(workflow=None, teams=None, exit_code=None, user=None, worker=None, quantity=None):
    """returns a queryset of workflow-logs filtered by given parameters"""
    _filter = {}
    if workflow:
        _filter['workflow'] = workflow
    if teams:
        _filter['workflow__owner__in'] = teams
    if user:
        _filter['performed_by'] = user
    if worker:
        _filter['performed_on'] = worker

    logs = WorkflowLog.objects.filter(**_filter).select_related('workflow', 'performed_by', 'performed_on')[:quantity]
    return logs


def has_admin_permission(user, organization):
    if OrganizationUser.objects.filter(organization=organization, user=user, is_admin=True).exists():
        return True
    else:
        return False


@login_required
def get_curr_org(request):
    org = Organization.objects.get(slug="3bot")  # request.user)
    request.session['currOrg'] = org.slug
    request.session.modified = True
    return org


@login_required
def get_my_orgs(request, an_user=None):
    if request is not None and an_user is None:
        an_user = request.user

    default_org, created = Organization.objects.get_or_create(slug='3bot', name="3bot")

    if not OrganizationUser.objects.filter(organization=default_org, user=an_user).exists():
        # we create an OrganizationUser, so each user is member of our default_org
        # if default_org was just created, we also mark this user as admin and create an OrganizationOwner
        org_user = OrganizationUser(organization=default_org, user=an_user, is_admin=created)
        org_user.save()
        if created:
            org_owner = OrganizationOwner(organization=default_org, organization_user=org_user)
            org_owner.save()

    orgs = Organization.objects.filter(users=an_user)

    return orgs


@login_required
def get_possible_owners(request):
    return get_my_orgs(request)


@login_required
def get_possible_parameters(request, workflow_task, data_type="string"):
    params = [('prompted.string.askme', '--Ask Me--')]
    user = request.user
    user_params = UserParameter.objects.all().filter(owner=user, data_type=data_type)
    org_params = OrganizationParameter.objects.all().filter(owner=workflow_task.workflow.owner, data_type=data_type)

    for param in user_params:
        params.append(("user.%s.%s" % (param.data_type, param.name), "user: %s" % param.name))

    for param in org_params:
        params.append(("global.%s.%s" % (param.data_type, param.name), "team: %s" % param.name))

    current = workflow_task
    # append all outputs from previous workflow tasks
    while current.prev_workflow_task:
        current = current.prev_workflow_task
        params.append(("output.string.output_%s" % current.id, "output: %s" % current.task.title))

    return tuple(params)


def get_possible_lists(request, workflow):
    return ParameterList.objects.all().filter(owner=workflow.owner).values_list('id', 'title').order_by('title')


@login_required
def get_preset_param(request, workflow_task, name, data_type="string"):
    # search the workflowpreset profile for the variable
    wf_preset, created = WorkflowPreset.objects.get_or_create(user=request.user, workflow=workflow_task.workflow)
    try:
        return wf_preset.defaults[str(workflow_task.id)]["%s.%s" % (data_type, name)]
    except KeyError:
        return None


@login_required
def get_possible_worker(request, as_list=False):
    orgs = get_my_orgs(request)
    if as_list:
        return Worker.objects.filter(owner__in=orgs).values_list('id', 'title')
    return Worker.objects.filter(owner__in=orgs)


@login_required
def get_preset_worker(request, workflow, flat=False):
    """
    returns a Worker queryset or a list of ids (flat = True),
    which a workflow recently was performed on by request.user.
    """
    # find or create the workflowpreset
    wf_preset, created = WorkflowPreset.objects.get_or_create(user=request.user, workflow=workflow)

    try:
        worker_ids = wf_preset.defaults["worker_id"]
    except (KeyError):
        worker_ids = []

    # backwards compatibility
    if isinstance(worker_ids, int) or isinstance(worker_ids, str):
        worker_ids = [worker_ids]

    if flat:
        return worker_ids

    return Worker.objects.filter(id__in=worker_ids)


@login_required
def get_preset_list(request, workflow, id=False):
    # search the workflowpreset
    wf_preset, created = WorkflowPreset.objects.get_or_create(user=request.user, workflow=workflow)
    try:
        list_id = wf_preset.defaults["list_id"]
        if id:
            return list_id
        return ParameterList.objects.get(id=list_id)
    except (KeyError, Worker.DoesNotExist):
        pass
    return None


def get_from_dict(dataDict, mapList):
    try:
        return reduce(lambda d, k: d[k], mapList, dataDict)
    except KeyError:
        return None


def set_in_dict(dataDict, mapList, value):
    get_from_dict(dataDict, mapList[:-1])[mapList[-1]] = value


def order_workflow_tasks(workflow):
    try:
        curr = workflow.workflowtask_set.get(prev_workflow_task=None)
        workflow_tasks = [curr]
        while curr.next_workflow_task:
            curr = curr.next_workflow_task
            workflow_tasks.append(curr)
    except WorkflowTask.DoesNotExist:
        workflow_tasks = []

    return workflow_tasks


def create_workflow_with(task):
    workflow = Workflow(slug="", title="Workflow from: %s" % task.title, owner=task.owner, desc="auto created", pre_task="", post_task="")
    workflow.save()

    wf_task = WorkflowTask(workflow=workflow, task=task)
    wf_task.save()
    return workflow


def clone_task_for_team(user, task, team):
    # check if user is member in both teams
    if user in team.users.all() and user in task.owner.users.all():
        if not task.is_builtin and not task.is_readonly:
            cloned_task = Task(owner=team, title=task.title, desc=task.desc, template=task.template, is_builtin=task.is_builtin, is_readonly=task.is_readonly)
            cloned_task.save()
            return cloned_task
        else:
            # user need admin permission to clone this task
            if has_admin_permission(user, task.owner):
                cloned_task = Task(owner=team, title=task.title, desc=task.desc, template=task.template, is_builtin=task.is_builtin, is_readonly=task.is_readonly)
                cloned_task.save()
                return cloned_task

    raise Exception("%s is not allowed to clone Task: %s (id: %i)" % (user.username, task, task.id))


def render_templates(workflow_log, mask=False):
    # mask = True -> hide templates on buildin or readonly tasks, replace sensitive data like passwords
    templates = []

    for wf_task in order_workflow_tasks(workflow_log.workflow):
        if mask:
            if wf_task.task.is_readonly or wf_task.task.is_builtin:
                # dont show template
                tpl = "No Template. Task is either built-in or readonly"
            else:
                # show template but hide sensitive data
                tpl = render_template(workflow_log, wf_task, mask=True)
        else:
            tpl = render_template(workflow_log, wf_task)
        templates.append(tpl)

    return templates


def render_template(workflow_log, workflow_task, mask=False):
    # mask = True -> replace sensitive data like passwords
    inputs = workflow_log.inputs[str(workflow_task.id)]

    if mask and 'password' in inputs:
        # replace sensitive data with '***'
        for key, value in inputs['password'].iteritems():
            inputs['password'][key] = '***'

    # Update reserved identifiers /keywords
    inputs['payload'] = workflow_log.inputs.get('payload', {})
    inputs['log'] = {}
    inputs['log']['url'] = workflow_log.get_absolute_url()
    # TODO: provide more information and document this type of inputs in knowledge base

    # Script/tempate rendering
    wf_context = Context(inputs)
    unrendered = workflow_task.task.template
    template = Template(unrendered)
    rendered = template.render(wf_context)
    return rendered


def importCode(code, name, add_to_sys_modules=0):
    """
    Import dynamically generated code as a module. code is the
    object containing the code (a string, a file handle or an
    actual compiled code object, same types as accepted by an
    exec statement). The name is the name to give to the module,
    and the final argument says wheter to add it to sys.modules
    or not. If it is added, a subsequent import statement using
    name will return this module. If it is not added to sys.modules
    import will try to load it in the normal fashion.

    import foo

    is equivalent to

    foofile = open("/path/to/foo.py")
    foo = importCode(foofile,"foo",1)

    Returns a newly generated module.
    """
    import sys
    import imp

    module = imp.new_module(name)

    exec(code)
    if add_to_sys_modules:
        sys.modules[name] = module

    return module
