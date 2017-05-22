from django import forms
from django.forms.models import modelformset_factory
from django.utils.safestring import mark_safe
from organizations.models import Organization
from organizations.utils import create_organization

from threebot.utils import get_possible_parameters, get_possible_worker, get_curr_org
from threebot.utils import get_preset_param, get_preset_worker, get_possible_owners, get_possible_lists, get_preset_list
from threebot.models import Worker
from threebot.models import Workflow
from threebot.models import Task
from threebot.models import UserParameter, OrganizationParameter, ParameterList
from threebot.utils import order_workflow_tasks


class UserParameterCreateForm(forms.ModelForm):
    next = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = UserParameter
        fields = ['data_type', 'name', 'value', 'owner', ]
        widgets = {
            'data_type': forms.Select(attrs={'class': 'form-control', }),
            'name': forms.TextInput(attrs={'class': 'form-control', }),
            'value': forms.TextInput(attrs={'class': 'form-control', }),
            'owner': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(UserParameterCreateForm, self).__init__(*args, **kwargs)
        self.fields['owner'].initial = user


class UserParameterChangeForm(UserParameterCreateForm):
    class Meta(UserParameterCreateForm.Meta):
        exclude = ('owner',)


class OrganizationParameterCreateForm(forms.ModelForm):
    class Meta:
        model = OrganizationParameter
        fields = ['data_type', 'name', 'value', 'owner', ]
        widgets = {
            'data_type': forms.Select(attrs={'class': 'form-control', }),
            'name': forms.TextInput(attrs={'class': 'form-control', }),
            'value': forms.TextInput(attrs={'class': 'form-control', }),
            'owner': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        org = kwargs.pop('org')
        super(OrganizationParameterCreateForm, self).__init__(*args, **kwargs)
        self.fields['owner'].initial = org


class OrganizationParameterChangeForm(OrganizationParameterCreateForm):
    class Meta(OrganizationParameterCreateForm.Meta):
        exclude = ('owner',)


def make_organization_parameter_formset(org, extra=3):
    """
    This is a workaround for passing custom parameters (the parameter owner in our case)
    to a ModelFormset and is based on this stackoverflow answer:
    http://stackoverflow.com/a/1376616
    """
    class _OrganizationParameterCreateForm(forms.ModelForm):
        remove_from_list = forms.BooleanField(required=False)

        class Meta:
            model = OrganizationParameter
            fields = ['data_type', 'name', 'value', 'owner', ]
            widgets = {
                'data_type': forms.Select(attrs={'class': 'form-control', }),
                'name': forms.TextInput(attrs={'class': 'form-control', }),
                'value': forms.TextInput(attrs={'class': 'form-control', }),
                'owner': forms.HiddenInput(),
            }

        def __init__(self, *args, **kwargs):
            # self.org = org
            super(_OrganizationParameterCreateForm, self).__init__(*args, **kwargs)
            self.fields['owner'].initial = org

    return modelformset_factory(OrganizationParameter, form=_OrganizationParameterCreateForm, extra=extra, can_delete=True)


def make_user_parameter_formset(user, extra=3):
    """
    This is a workaround for passing custom parameters (the parameter owner in our case)
    to a ModelFormset and is based on this stackoverflow answer:
    http://stackoverflow.com/a/1376616
    """
    class _UserParameterCreateForm(forms.ModelForm):
        class Meta:
            model = UserParameter
            fields = ['data_type', 'name', 'value', 'owner', ]
            widgets = {
                'data_type': forms.Select(attrs={'class': 'form-control', }),
                'name': forms.TextInput(attrs={'class': 'form-control', }),
                'value': forms.TextInput(attrs={'class': 'form-control', }),
                'owner': forms.HiddenInput(),
            }

        def __init__(self, *args, **kwargs):
            # user = kwargs.pop('user')
            super(_UserParameterCreateForm, self).__init__(*args, **kwargs)
            self.fields['owner'].initial = user

    return modelformset_factory(UserParameter, form=_UserParameterCreateForm, extra=extra, can_delete=True)


class ParameterListSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        workflow = kwargs.pop('workflow')
        self.workflow = workflow

        super(ParameterListSelectForm, self).__init__(*args, **kwargs)

        possible_lists = [('', '--Choose a Parameter List--')]
        possible_lists += get_possible_lists(request, workflow)
        preset_list_id = get_preset_list(request, workflow, id=True)

        self.fields['parameter_list'] = forms.ChoiceField(
            label="Parameter List",
            choices=possible_lists,
            initial=preset_list_id,
            widget=forms.Select(attrs={'class': 'form-control', }),
        )
        self.fields['parameter_list'].empty_label = None

    def clean_parameter_list(self, *args, **kwargs):
        list_id = self.cleaned_data['parameter_list']
        parameter_list = ParameterList.objects.get(id=list_id)
        workflow_tasks = order_workflow_tasks(self.workflow)

        # make a list of ::all_required_inputs, with name and data type
        all_required_inputs = []
        for wf_task in workflow_tasks:
            for name, data_type in wf_task.task.required_inputs.iteritems():
                if name not in all_required_inputs:
                    all_required_inputs.append((name, data_type))

        # make a list of ::all_parameters from the list, with name and data type
        all_parameters = []
        for parameter in parameter_list.parameters.all():
            all_parameters.append((parameter.name, parameter.data_type))

        # if not every element of ::all_parameters is also in ::all_required_inputs
        # the list is not valid for this workflow, raise an form validation error
        if not False not in [e in all_parameters for e in all_required_inputs]:
            error_message = "Not all required inputs found in ParameterList."
            error_message += "<br><br><strong>Required inputs by the Tasks are</strong>:"
            for param in all_required_inputs:
                error_message += "<br>" + str(param[0]) + ":" + str(param[1])

            error_message += "<br><br><strong>List contains</strong>:"
            for param in all_parameters:
                error_message += "<br>" + str(param[0]) + ":" + str(param[1])
            raise forms.ValidationError(mark_safe(error_message))
        return list_id


class WorkerSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        workflow = kwargs.pop('workflow')

        super(WorkerSelectForm, self).__init__(*args, **kwargs)

        possible_workers = get_possible_worker(request, as_list=True)
        preset_worker = get_preset_worker(request, workflow, flat=True)

        self.fields['worker'] = forms.MultipleChoiceField(
            required=True,
            label="Worker",
            choices=possible_workers,
            initial=preset_worker,
            widget=forms.SelectMultiple(attrs={'class': 'form-control', }),
        )
        self.fields['worker'].empty_label = None

        # workaround for displaying a message to the user
        # if no worker is acessible while initializing the form
        if len(possible_workers) <= 0:
            self.cleaned_data = {}
            msg = "No Worker found. Please configure a Worker first."
            self.add_error('worker', msg)

    def clean(self):
        cleaned_data = super(WorkerSelectForm, self).clean()
        worker_ids = cleaned_data.get('worker', [])
        workers = Worker.objects.filter(id__in=worker_ids)
        for worker in workers:
            if not worker.is_accessible:
                raise forms.ValidationError("worker not accessible")
        # Always return the full collection of cleaned data.
        # This has changed in django 1.7 but raises errors in django <1.7
        # We want to support both, so we return cleanded_data
        return cleaned_data


class WorkerForm(forms.ModelForm):
    """Base Worker Form"""
    class Meta:
        model = Worker
        fields = ['title', 'ip', 'port', 'muted', 'secret_key', 'pre_task', 'post_task', ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'ip': forms.TextInput(attrs={'class': 'form-control', }),
            'addr': forms.TextInput(attrs={'class': 'form-control', 'rows': '5', }),
            'port': forms.TextInput(attrs={'class': 'form-control', }),
            'secret_key': forms.TextInput(attrs={'class': 'form-control', }),
            'pre_task': forms.Textarea(attrs={'class': 'form-control', 'rows': '5', }),
            'post_task': forms.Textarea(attrs={'class': 'form-control', 'rows': '5', }),
        }

    def __init__(self, *args, **kwargs):
        super(WorkerForm, self).__init__(*args, **kwargs)


class WorkerCreateForm(WorkerForm):
    """Form to create a Worker"""
    class Meta(WorkerForm.Meta):
        fields = ['owner', ] + WorkerForm.Meta.fields
        exclude = ['muted']
        WorkerForm.Meta.widgets['owner'] = forms.Select(attrs={'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(WorkerCreateForm, self).__init__(*args, **kwargs)
        self.fields['owner'].queryset = get_possible_owners(request)
        self.fields['owner'].initial = get_curr_org(request)


class WorkerChangeForm(WorkerForm):
    """Form to edit a Worker"""
    pass


class TaskForm(forms.ModelForm):
    """Base Task Form"""
    class Meta:
        model = Task
        fields = ['title', 'desc', 'template', 'changelog', 'is_readonly', ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'desc': forms.Textarea(attrs={'class': 'form-control', 'rows': '5', }),
            'template': forms.Textarea(attrs={'class': 'form-control', 'rows': '5', 'style': 'font-family:monospace;'}),
            'changelog': forms.Textarea(attrs={'class': 'form-control', 'rows': '5', }),
            'is_readonly': forms.CheckboxInput(attrs={}),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)


class TaskCreateForm(TaskForm):
    """Form to create a Task"""
    class Meta(TaskForm.Meta):
        fields = ['owner', ] + TaskForm.Meta.fields
        TaskForm.Meta.widgets['owner'] = forms.Select(attrs={'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(TaskCreateForm, self).__init__(*args, **kwargs)
        self.fields['owner'].queryset = get_possible_owners(request)
        self.fields['owner'].initial = get_curr_org(request)


class TaskChangeForm(TaskForm):
    """Form to edit a Task"""
    pass


class TaskImportForm(forms.Form):
    """Form to import a Task"""
    task_json = forms.FileField()


class WorkflowForm(forms.ModelForm):
    """Base Workflow Form"""
    class Meta:
        model = Workflow
        fields = ['title', 'desc', 'pre_task', 'post_task', ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'desc': forms.Textarea(attrs={'class': 'form-control', 'rows': '5', }),
            'pre_task': forms.Textarea(attrs={'class': 'form-control', 'rows': '5', }),
            'post_task': forms.Textarea(attrs={'class': 'form-control', 'rows': '5', }),
        }

    def __init__(self, *args, **kwargs):
        super(WorkflowForm, self).__init__(*args, **kwargs)


class WorkflowCreateForm(WorkflowForm):
    """Form to create a Workflow"""
    class Meta(WorkflowForm.Meta):
        fields = ['owner', ] + WorkflowForm.Meta.fields
        WorkflowForm.Meta.widgets['owner'] = forms.Select(attrs={'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(WorkflowCreateForm, self).__init__(*args, **kwargs)
        self.fields['owner'].queryset = get_possible_owners(request)
        self.fields['owner'].initial = get_curr_org(request)


class WorkflowChangeForm(WorkflowForm):
    """Form to edit a Workflow"""
    pass


class WorkflowReorderForm(forms.Form):
    workflow_id = forms.CharField(max_length=30, widget=forms.HiddenInput())
    order = forms.CharField(widget=forms.HiddenInput())


class TaskParameterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        extra = kwargs.pop('extra')
        workflow_task = kwargs.pop('workflow_task')
        super(TaskParameterForm, self).__init__(*args, **kwargs)

        for name, data_type in extra.iteritems():
            possible_parameters = get_possible_parameters(request, workflow_task, data_type)
            preset_parameter = get_preset_param(request, workflow_task, name, data_type)
            self.fields['wt_task_%i.%s.%s' % (workflow_task.id, data_type, name)] = forms.ChoiceField(
                label="%s (%s)" % (name, data_type),
                choices=possible_parameters,
                initial=preset_parameter,
                widget=forms.Select(attrs={'class': 'form-control', }),
                )

            # each param gets a hidden field for saving prompted data
            self.fields['prompt_wt_task_%i.%s.%s' % (workflow_task.id, data_type, name)] = forms.CharField(widget=forms.HiddenInput(), required=False, )


class OrganizationCreateForm(forms.ModelForm):
    """
    Form class for creating a new organization, complete with new owner, including a
    User instance, OrganizationUser instance, and OrganizationOwner instance.
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(OrganizationCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Organization
        exclude = ('users', 'is_active',)

    def save(self, **kwargs):
        """
        Create the organization, then get the user, then make the owner.
        """
        user = self.request.user
        return create_organization(user, self.cleaned_data['name'], self.cleaned_data['slug'], is_active=True)
