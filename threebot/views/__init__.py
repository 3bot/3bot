from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.template import RequestContext
from django.conf import settings

from organizations.models import Organization

from threebot.models import Workflow
from threebot.utils import get_my_orgs, filter_workflow_log_history


@login_required
def orgswitcher(request, slug):
    org = Organization.objects.get(users=request.user, slug=slug)
    request.session['currOrg'] = org
    request.session.modified = True
    return HttpResponseRedirect("/")  # FIXME: correct path, lang


@login_required
def chooseorg(request, template='threebot/chooseorg.html'):
    orgs = Organization.objects.filter(users=request.user)

    return render_to_response(template, {'request': request,
                                         'orgs': orgs,
                                        }, context_instance=RequestContext(request))


def user_login(request, template='threebot/login.html'):
    next = request.GET.get("next", getattr(settings, "LOGIN_REDIRECT_URL", "/"))
    auth_form = AuthenticationForm(None, request.POST or None)

    if request.user.is_authenticated():
        # no need to login again, just redirect
        return redirect(next)

    if auth_form.is_valid():
        # The form itself handles authentication and checking to make sure passowrd and such are supplied.
        next = request.POST.get("next", getattr(settings, "LOGIN_REDIRECT_URL", "/"))
        login(request, auth_form.get_user())
        return HttpResponseRedirect(next)

    return render_to_response(template, {'request': request,
                                         'auth_form': auth_form,
                                        }, context_instance=RequestContext(request))


def user_logout(request):
    logout(request)
    return redirect("/")


@login_required
def index(request, template='threebot/index.html'):
    org_ids = get_my_orgs(request).values_list('id', flat=True)
    team_logs = WorkflowLog.objects.filter(workflow__owner_id__in=org_ids).values(
        'id', 'exit_code', 'workflow__title', 'date_created',
        'performed_by__username', 'performed_on__id' 'performed_on__title',
    )
    return render_to_response(template, {'request': request,
                                         'team_logs': team_logs,
                                        }, context_instance=RequestContext(request))
