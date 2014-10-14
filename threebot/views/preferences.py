from django.shortcuts import redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from organizations.models import Organization, OrganizationUser

from ..models import OrganizationParameter
from ..models import UserParameter
from ..forms import UserParameterCreateForm, OrganizationParameterCreateForm, OrganizationCreateForm


@login_required
def user_profile(request, template='threebot/preferences/user/profile.html'):
    return render_to_response(template, {'request': request,
                                         'profile': True,
                                        }, context_instance=RequestContext(request))


@login_required
def user_parameter(request, template='threebot/preferences/user/parameter.html'):
    user_parameter = UserParameter.objects.all().filter(owner=request.user)
    form = UserParameterCreateForm(request.POST or None, user=request.user)

    if form.is_valid():
        form.save()
        if 'next' in form.cleaned_data:
            return HttpResponseRedirect(form.cleaned_data['next'])

    return render_to_response(template, {'request': request,
                                         'parameter_list': user_parameter,
                                         'form': form,
                                         'parameter': True,
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
                                         'parameter': True,
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

    #checks if we have access
    get_object_or_404(OrganizationUser, organization=organization, user=request.user, is_admin=True)

    organization_parameter = OrganizationParameter.objects.filter(owner=organization)
    form = OrganizationParameterCreateForm(request.POST or None, org=organization)

    if form.is_valid():
        form.save()

    return render_to_response(template, {'request': request,
                                         'organization': organization,
                                         'parameter_list': organization_parameter,
                                         'form': form,
                                         'parameter': True,
                                        }, context_instance=RequestContext(request))


@login_required
def organization_parameter_detail(request, slug, id, template='threebot/preferences/user/parameter_detail.html'):
    organization = get_object_or_404(Organization, slug=slug)

    #checks if we have access
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

    #checks if we have access
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
