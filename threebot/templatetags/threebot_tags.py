from django import template
from threebot import __version__
from ..utils import get_my_orgs, get_preset_worker, has_admin_permission
from ..models import WorkflowPreset

register = template.Library()


@register.inclusion_tag('threebot/my_orgs.html')
def show_my_orgs(request):
    orgs = get_my_orgs(request)
    return {'orgs': orgs}


@register.filter
def can_be_administarated_by(organization, user):
    if user is None:
        return False
    return has_admin_permission(user, organization)


@register.assignment_tag
def get_last_worker_for(request, workflow):
    if workflow is None:
        return None

    return get_preset_worker(request, workflow)


@register.assignment_tag
def my_teams(request, excusion_tag=None):
    my_teams = get_my_orgs(request)
    if excusion_tag:
        my_teams = my_teams.exclude(slug=excusion_tag)
    return my_teams


@register.assignment_tag
def get_presets_for(request, workflow):
    if workflow is None:
        return None

    return WorkflowPreset.objects.get(workflow=workflow, user=request.user)


@register.assignment_tag
def get_threebot_version():
    return __version__
