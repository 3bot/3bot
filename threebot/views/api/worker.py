from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from threebot.models import Worker
from threebot.utils import get_my_orgs


@login_required
def detail(request, id):
    orgs = get_my_orgs(request)
    worker = get_object_or_404(Worker, owner__in=orgs, id=id)

    return JsonResponse({
        'id': worker.id,
        'status': worker.status,
        'status_display': worker.get_status_display(),
    })
