from django.contrib import admin

from .models import Worker
from .models import Task
from .models import Workflow
from .models import WorkflowTask
from .models import WorkflowLog
from .models import WorkflowPreset
from .models import UserParameter
from .models import OrganizationParameter
from .models import ParameterList


class WorkerAdmin(admin.ModelAdmin):
    model = Worker
    readonly_fields = ('slug', 'is_accessible', )


class WorkflowPresetAdmin(admin.ModelAdmin):
    model = WorkflowPreset
    list_display = ('workflow', 'user', 'date_created', 'date_modified', )


class TaskAdmin(admin.ModelAdmin):
    model = Task
    readonly_fields = ('slug', 'required_inputs', 'inputs_fingerprint', 'version', )


class WorkflowAdmin(admin.ModelAdmin):
    model = Workflow
    readonly_fields = ('slug', )


class WorkflowLogAdmin(admin.ModelAdmin):
    model = WorkflowLog
    list_display = ('workflow', 'date_created', 'exit_code', 'performed_by', )
    list_filter = ('exit_code',)


class WorkflowTaskAdmin(admin.ModelAdmin):
    model = WorkflowTask


class UserParameterAdmin(admin.ModelAdmin):
    model = UserParameter
    list_display = ('name', 'data_type', 'value', 'owner', )
    list_filter = ('data_type', )


class OrganizationParameterAdmin(UserParameterAdmin):
    "We just inherit from UserParameterAdmin, sinze we use the same base Model"
    pass


class ParameterListAdmin(admin.ModelAdmin):
    model = ParameterList
    list_display = ('title', 'owner', 'date_created', 'date_modified')
    list_filter = ('owner', )


admin.site.register(UserParameter, UserParameterAdmin)
admin.site.register(OrganizationParameter, OrganizationParameterAdmin)
admin.site.register(ParameterList, ParameterListAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(WorkflowTask, WorkflowTaskAdmin)
admin.site.register(WorkflowLog, WorkflowLogAdmin)
admin.site.register(WorkflowPreset, WorkflowPresetAdmin)
