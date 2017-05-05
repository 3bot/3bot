from django.conf.urls import url, include

from organizations.backends import invitation_backend
import views


urlpatterns = [
    url(r'^worker/add/$', views.worker.create, name='core_worker_create'),
    url(r'^worker/(?P<slug>[-\w]+)/delete/$', views.worker.delete, name='core_worker_delete'),
    url(r'^worker/(?P<slug>[-\w]+)/manual/$', views.worker.detail_manual, name='core_worker_detail_manual'),
    url(r'^worker/(?P<slug>[-\w]+)/digest/$', views.worker.detail_digest, name='core_worker_detail_digest'),
    url(r'^worker/(?P<slug>[-\w]+)/$', views.worker.detail_edit, name='core_worker_detail'),
    url(r'^worker/$', views.worker.list, name='core_worker_list'),
    url(r'^wk/(?P<id>[-\w]+)/$', views.worker.worker_permalink, name='core_worker_permalink'),

    url(r'^task/add/$', views.task.create, name='core_task_create'),
    url(r'^task/import/$', views.task.import_task, name='core_task_import'),
    url(r'^task/clone/(?P<taskslug>[-\w]+)-(?P<teamslug>[-\w]+)/$', views.task.clone_for_team, name='core_task_clone'),
    url(r'^task/(?P<slug>[-\w]+)/new_workflow/$', views.task.create_workflow, name='core_task_create_workflow'),
    url(r'^task/(?P<slug>[-\w]+)/delete/$', views.task.delete, name='core_task_delete'),
    url(r'^task/(?P<slug>[-\w]+)/export/$', views.task.export, name='core_task_export'),
    url(r'^task/(?P<slug>[-\w]+)/digest/$', views.task.detail_digest, name='core_task_detail_digest'),
    url(r'^task/(?P<slug>[-\w]+)/$', views.task.detail_edit, name='core_task_detail'),
    url(r'^task/$', views.task.list, name='core_task_list'),
    url(r'^t/(?P<id>[-\w]+)/$', views.task.task_permalink, name='core_task_permalink'),

    url(r'^workflow/add/$', views.workflow.create, name='core_workflow_create'),
    url(r'^workflow/(?P<slug>[-\w]+)/log/(?P<id>[-\w]+)/render/$', views.workflow.log_detail_render, name='core_workflow_log_detail_render'),
    url(r'^workflow/(?P<slug>[-\w]+)/log/(?P<id>[-\w]+)/$', views.workflow.log_detail, name='core_workflow_log_detail'),
    url(r'^workflow/(?P<slug>[-\w]+)/log/(?P<id>[-\w]+)/replay/$', views.workflow.replay, name='core_workflow_replay'),
    url(r'^workflow/(?P<slug>[-\w]+)/delete/$', views.workflow.delete, name='core_workflow_delete'),
    url(r'^workflow/(?P<slug>[-\w]+)/digest/$', views.workflow.detail_digest, name='core_workflow_detail_digest'),
    url(r'^workflow/(?P<slug>[-\w]+)/reorder/$', views.workflow.detail_reorder, name='core_workflow_detail_reorder'),
    url(r'^workflow/(?P<slug>[-\w]+)/edit/$', views.workflow.detail_edit, name='core_workflow_detail_edit'),
    url(r'^workflow/(?P<slug>[-\w]+)/with-list/$', views.workflow.detail_perf_with_list, name='core_workflow_detail_with_list'),
    url(r'^workflow/(?P<slug>[-\w]+)/$', views.workflow.detail_perf, name='core_workflow_detail'),
    url(r'^workflow/$', views.workflow.list, name='core_workflow_list'),
    url(r'^wf/(?P<id>[-\w]+)/$', views.workflow.workflow_permalink, name='core_workflow_permalink'),
    url(r'^log/(?P<id>[-\w]+)/$', views.workflow.workflow_log_permalink, name='core_workflow_log_permalink'),

    url(r'^user/parameter/(?P<id>[-\w]+)/delete/$', views.preferences.user_parameter_delete, name='core_user_parameter_delete'),
    url(r'^user/parameter/(?P<id>[-\w]+)/$', views.preferences.user_parameter_detail, name='core_user_parameter_detail'),
    url(r'^user/parameter/$', views.preferences.user_parameter, name='core_user_parameter'),
    url(r'^user/activity/$', views.preferences.user_activity, name='core_user_activity'),
    url(r'^user/$', views.preferences.user_profile, name='core_user_profile'),

    url(r'^teams/add/$', views.preferences.organization_add, name='core_organization_add'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/(?P<id>[-\w]+)/delete/$', views.preferences.organization_parameter_delete, name='core_organization_parameter_delete'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/(?P<id>[-\w]+)/$', views.preferences.organization_parameter_detail, name='core_organization_parameter_detail'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/list/(?P<list_id>[-\w]+)/$', views.preferences.organization_parameter_list, name='core_organization_parameter_list'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/$', views.preferences.organization_parameter, name='core_organization_parameter'),
    url(r'^teams/(?P<slug>[-\w]+)/activity/$', views.preferences.organitazion_activity, name='core_organization_activity'),
    url(r'^teams/', include('organizations.urls')),

    url(r'^invitations/', include(invitation_backend().get_urls())),

    url(r'^chooseorg/$', views.base.chooseorg),
    url(r'^login/$', views.base.user_login, name='auth_login'),
    url(r'^logout/$', views.base.user_logout, name='auth_logout'),
    url(r'^orgswitcher/(?P<slug>[-\w]+)/$', views.base.orgswitcher),
    url(r'^$', views.base.index, name='core_index'),

    ### API ###
    url(r'^api/workers/(?P<id>[-\d]+)/$', views.api.worker.detail, name='api_worker_detail'),
    url(r'^api/logs/(?P<id>[-\d]+)/$', views.api.log.detail, name='api_log_detail'),
]
