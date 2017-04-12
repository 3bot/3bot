from django.contrib import admin

from threebot.models import Worker
from threebot.models import Task
from threebot.models import Workflow
from threebot.models import WorkflowTask
from threebot.models import WorkflowLog
from threebot.models import WorkflowPreset
from threebot.models import UserParameter
from threebot.models import OrganizationParameter
from threebot.models import ParameterList


class WorkerAdmin(admin.ModelAdmin):
    model = Worker
    readonly_fields = ('slug', )
    list_display = ('title', 'slug', 'owner', 'ip', 'port', 'muted', )
    list_filter = ('muted', 'owner__name', )
    search_fields = ['owner__name', 'title', 'slug', ]


class WorkflowPresetAdmin(admin.ModelAdmin):
    model = WorkflowPreset
    list_display = ('workflow', 'user', 'date_created', 'date_modified', )


class TaskAdmin(admin.ModelAdmin):
    model = Task
    readonly_fields = ('slug', 'required_inputs', 'inputs_fingerprint', 'version', 'unique_identifier', )
    list_display = ('title', 'slug', 'owner', 'is_readonly', 'is_builtin', )
    list_filter = ('is_readonly', 'is_builtin', 'owner__name', )
    search_fields = ['owner__name', 'title', 'slug', 'unique_identifier', ]


class WorkflowAdmin(admin.ModelAdmin):
    model = Workflow
    readonly_fields = ('slug', )
    list_display = ('title', 'slug', 'owner', )
    list_filter = ('owner__name', )
    search_fields = ['owner__name', 'title', 'slug', ]


class WorkflowLogAdmin(admin.ModelAdmin):
    model = WorkflowLog
    list_display = ('workflow', 'date_created', 'exit_code', 'performed_by', )
    list_filter = ('exit_code',)
    search_fields = ['workflow__title', ]
    actions = ['make_errored']

    def make_failed(self, request, queryset):
        queryset.update(exit_code=self.model.ERROR)
    make_failed.short_description = "Mark selected logs as failed"


class WorkflowTaskAdmin(admin.ModelAdmin):
    model = WorkflowTask
    list_display = ('task', 'prev_workflow_task', 'next_workflow_task', )
    search_fields = ['task__title', ]


class UserParameterAdmin(admin.ModelAdmin):
    model = UserParameter
    list_display = ('name', 'data_type', 'value', 'owner', )
    list_filter = ('data_type', )


class OrganizationParameterAdmin(UserParameterAdmin):
    "Since we use the same base Model, we just inherit from UserParameterAdmin"
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
