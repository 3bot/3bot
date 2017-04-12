from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from threebot.models import WorkflowLog
from threebot.utils import get_my_orgs


@login_required
def detail(request, id):
    orgs = get_my_orgs(request)
    log = get_object_or_404(WorkflowLog, id=id)

    return JsonResponse({
        'id': log.id,
        'exit_code': log.exit_code,
        'exit_code_display': log.get_exit_code_display(),
    })
