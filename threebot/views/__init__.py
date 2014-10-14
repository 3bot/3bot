from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.template import RequestContext

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
    if request.user.is_authenticated():
        return redirect("/")

    auth_form = AuthenticationForm(None, request.POST or None)

    nextpage = request.GET.get('next', '/')
    # The form itself handles authentication and checking to make sure passowrd and such are supplied.
    if auth_form.is_valid():
        login(request, auth_form.get_user())
        return HttpResponseRedirect(nextpage)

    return render_to_response(template, {'request': request,
                                         'auth_form': auth_form,
                                        }, context_instance=RequestContext(request))


def user_logout(request):
    logout(request)
    return redirect("/")


@login_required
def index(request, template='threebot/index.html'):
    orgs = get_my_orgs(request)

    counts = Workflow.objects.filter(owner__in=orgs).annotate(issue_count=Count('workflowlog')).order_by('-issue_count')
    counts = counts.filter(issue_count__gte=1)[:5]
    team_logs = filter_workflow_log_history(teams=orgs, quantity=5)
    my_logs = filter_workflow_log_history(teams=orgs, user=request.user, quantity=5)

    return render_to_response(template, {'request': request,
                                         'counts': counts,
                                         'team_logs': team_logs,
                                         'my_logs': my_logs,
                                        }, context_instance=RequestContext(request))
