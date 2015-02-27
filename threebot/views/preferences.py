from django.shortcuts import redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist

from organizations.models import Organization, OrganizationUser

from threebot.models import OrganizationParameter, UserParameter, ParameterList
from threebot.forms import (
    UserParameterCreateForm,
    OrganizationParameterCreateForm,
    OrganizationCreateForm,
    make_organization_parameter_formset,
    make_user_parameter_formset)
from threebot.utils import filter_workflow_log_history


@login_required
def user_profile(request, template='threebot/preferences/user/profile.html'):
    token = ""

    try:
        from rest_framework.authtoken.models import Token
        token = Token.objects.get(user=request.user)
    except (ImportError, ObjectDoesNotExist):
        pass
    return render_to_response(template, {'request': request,
                                         'token': token,
                                        }, context_instance=RequestContext(request))


@login_required
def user_parameter(request, template='threebot/preferences/user/parameter.html'):
    user_parameter = UserParameter.objects.all().filter(owner=request.user)

    ParamFormset = make_user_parameter_formset(request.user)
    formset = ParamFormset(
        request.POST or None,
        queryset=user_parameter,
    )

    if formset.is_valid():
        formset.save()

        user_parameter = UserParameter.objects.all().filter(owner=request.user)
        formset = ParamFormset(queryset=user_parameter)

    return render_to_response(template, {'request': request,
                                         'formset': formset,
                                        }, context_instance=RequestContext(request))


@login_required
def user_activity(request, template='threebot/preferences/user/activity.html'):
    logs = filter_workflow_log_history(user=request.user, quantity=20)
    return render_to_response(template, {'request': request,
                                         'logs': logs
                                        }, context_instance=RequestContext(request))


@login_required
def user_parameter_detail(request, id, template='threebot/preferences/user/parameter_detail.html'):
    user_parameter = UserParameter.objects.get(id=id)
    form = UserParameterCreateForm(request.POST or None, user=request.user, instance=user_parameter)

    if form.is_valid():
        form.save()

    return render_to_response(template, {'request': request,
                                         'param': user_parameter,
                                         'form': form,
                                        }, context_instance=RequestContext(request))


@login_required
def organization_add(request, template='threebot/preferences/organization/create.html'):
    form = OrganizationCreateForm(request.POST or None, request=request)

    if form.is_valid():
        org = form.save()
        return redirect('organization_detail', organization_pk=org.id)

    return render_to_response(template, {'request': request,
                                         'form': form,
                                        }, context_instance=RequestContext(request))


@login_required
def user_parameter_delete(request, id, template='threebot/preferences/user/parameter_delete.html'):
    param = get_object_or_404(UserParameter, owner=request.user, id=id)

    if request.method == 'POST':
        new_data = request.POST.copy()
        if new_data['delete_param'] == 'Yes':
            param.delete()
            return redirect('core_user_parameter')
        else:
            return redirect('core_user_parameter_detail', id=param.id)

    return render_to_response(template, {'param': param,
                                        }, context_instance=RequestContext(request))


@login_required
def organization_parameter(request, slug, template='threebot/preferences/organization/parameter.html'):
    organization = get_object_or_404(Organization, slug=slug)

    # checks if we have access
    get_object_or_404(OrganizationUser, organization=organization, user=request.user, is_admin=True)

    organization_parameter = OrganizationParameter.objects.filter(owner=organization)
    ParamFormset = make_organization_parameter_formset(organization)
    formset = ParamFormset(
        request.POST or None,
        queryset=organization_parameter
    )

    if formset.is_valid():
        formset.save()
        organization_parameter = OrganizationParameter.objects.filter(owner=organization)
        formset = ParamFormset(queryset=organization_parameter)

    return render_to_response(template, {'request': request,
                                         'organization': organization,
                                         'formset': formset,
                                         'lists': ParameterList.objects.filter(owner=organization)
                                        }, context_instance=RequestContext(request))


@login_required
def organization_parameter_list(request, slug, list_id, template='threebot/preferences/organization/parameter_list.html'):
    organization = get_object_or_404(Organization, slug=slug)

    # checks if we have access
    get_object_or_404(OrganizationUser, organization=organization, user=request.user, is_admin=True)

    p_list = ParameterList.objects.get(id=list_id)
    organization_parameter = p_list.parameters.all()
    ParamFormset = make_organization_parameter_formset(organization)
    formset = ParamFormset(
        request.POST or None,
        queryset=organization_parameter
    )

    if formset.is_valid():
        parameter = formset.save()
        for param in parameter:
            p_list.parameters.add(param)

        for form in formset:
            if form.cleaned_data.get('remove_from_list'):
                p_list.parameters.remove(form.instance)

        # catch updated list items
        p_list = ParameterList.objects.get(id=list_id)
        organization_parameter = p_list.parameters.all()
        ParamFormset = make_organization_parameter_formset(organization)
        formset = ParamFormset(queryset=organization_parameter)

    return render_to_response(template, {'request': request,
                                         'organization': organization,
                                         'parameter_list': organization_parameter,
                                         'formset': formset,
                                         'list': p_list,
                                        }, context_instance=RequestContext(request))


@login_required
def organization_parameter_detail(request, slug, id, template='threebot/preferences/user/parameter_detail.html'):
    organization = get_object_or_404(Organization, slug=slug)

    # checks if we have access
    get_object_or_404(OrganizationUser, organization=organization, user=request.user, is_admin=True)

    organization_parameter = OrganizationParameter.objects.get(owner=organization, id=id)
    form = OrganizationParameterCreateForm(request.POST or None, org=organization, instance=organization_parameter)

    if form.is_valid():
        form.save()

    return render_to_response(template, {'request': request,
                                         'param': organization_parameter,
                                         'form': form,
                                         'parameter': True,
                                        }, context_instance=RequestContext(request))


@login_required
def organization_parameter_delete(request, slug, id, template='threebot/preferences/user/parameter_delete.html'):
    organization = get_object_or_404(Organization, slug=slug)

    # checks if we have access
    get_object_or_404(OrganizationUser, organization=organization, user=request.user, is_admin=True)

    param = OrganizationParameter.objects.get(owner=organization, id=id)

    if request.method == 'POST':
        new_data = request.POST.copy()
        if new_data['delete_param'] == 'Yes':
            param.delete()
            return redirect('core_organization_parameter')
        else:
            return redirect('core_organization_parameter_detail', slug=slug, id=param.id)

    return render_to_response(template, {'param': param,
                                        }, context_instance=RequestContext(request))


@login_required
def organitazion_activity(request, slug, template='threebot/preferences/organization/activity.html'):
    organization = get_object_or_404(Organization, slug=slug)
    organizations = [].append(organization)

    # checks if we have access
    get_object_or_404(OrganizationUser, organization=organization, user=request.user, is_admin=True)

    logs = filter_workflow_log_history(teams=organizations, quantity=20)
    return render_to_response(template, {'request': request,
                                         'organization': organization,
                                         'logs': logs
                                        }, context_instance=RequestContext(request))
