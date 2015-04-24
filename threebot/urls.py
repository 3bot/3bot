from django.conf.urls import patterns, url, include

from organizations.backends import invitation_backend


urlpatterns = patterns(
    'threebot.views',
    url(r'^worker/add/$', view='worker.create', name='core_worker_create'),
    url(r'^worker/(?P<slug>[-\w]+)/delete/$', view='worker.delete', name='core_worker_delete'),
    url(r'^worker/(?P<slug>[-\w]+)/manual/$', view='worker.detail_manual', name='core_worker_detail_manual'),
    url(r'^worker/(?P<slug>[-\w]+)/digest/$', view='worker.detail_digest', name='core_worker_detail_digest'),
    url(r'^worker/(?P<slug>[-\w]+)/$', view='worker.detail_edit', name='core_worker_detail'),
    url(r'^worker/$', view='worker.list', name='core_worker_list'),

    url(r'^task/add/$', view='task.create', name='core_task_create'),
    url(r'^task/import/$', view='task.import_task', name='core_task_import'),
    url(r'^task/clone/(?P<taskslug>[-\w]+)-(?P<teamslug>[-\w]+)/$', view='task.clone_for_team', name='core_task_clone'),
    url(r'^task/(?P<slug>[-\w]+)/new_workflow/$', view='task.create_workflow', name='core_task_create_workflow'),
    url(r'^task/(?P<slug>[-\w]+)/delete/$', view='task.delete', name='core_task_delete'),
    url(r'^task/(?P<slug>[-\w]+)/export/$', view='task.export', name='core_task_export'),
    url(r'^task/(?P<slug>[-\w]+)/digest/$', view='task.detail_digest', name='core_task_detail_digest'),
    url(r'^task/(?P<slug>[-\w]+)/$', view='task.detail_edit', name='core_task_detail'),
    url(r'^task/$', view='task.list', name='core_task_list'),

    url(r'^workflow/add/$', view='workflow.create', name='core_workflow_create'),
    url(r'^workflow/(?P<slug>[-\w]+)/log/(?P<id>[-\w]+)/render/$', view='workflow.log_detail_render', name='core_workflow_log_detail_render'),
    url(r'^workflow/(?P<slug>[-\w]+)/log/(?P<id>[-\w]+)/$', view='workflow.log_detail', name='core_workflow_log_detail'),
    url(r'^workflow/(?P<slug>[-\w]+)/log/(?P<id>[-\w]+)/replay/$', view='workflow.replay', name='core_workflow_replay'),
    url(r'^workflow/(?P<slug>[-\w]+)/delete/$', view='workflow.delete', name='core_workflow_delete'),
    url(r'^workflow/(?P<slug>[-\w]+)/digest/$', view='workflow.detail_digest', name='core_workflow_detail_digest'),
    url(r'^workflow/(?P<slug>[-\w]+)/reorder/$', view='workflow.detail_reorder', name='core_workflow_detail_reorder'),
    url(r'^workflow/(?P<slug>[-\w]+)/edit/$', view='workflow.detail_edit', name='core_workflow_detail_edit'),
    url(r'^workflow/(?P<slug>[-\w]+)/with-list/$', view='workflow.detail_perf_with_list', name='core_workflow_detail_with_list'),
    url(r'^workflow/(?P<slug>[-\w]+)/$', view='workflow.detail_perf', name='core_workflow_detail'),
    url(r'^workflow/$', view='workflow.list', name='core_workflow_list'),

    url(r'^log/(?P<id>[-\w]+)/$', view='workflow.redirect_to_log', ),

    url(r'^user/parameter/(?P<id>[-\w]+)/delete/$', view='preferences.user_parameter_delete', name='core_user_parameter_delete'),
    url(r'^user/parameter/(?P<id>[-\w]+)/$', view='preferences.user_parameter_detail', name='core_user_parameter_detail'),
    url(r'^user/parameter/$', view='preferences.user_parameter', name='core_user_parameter'),
    url(r'^user/activity/$', view='preferences.user_activity', name='core_user_activity'),
    url(r'^user/$', view='preferences.user_profile', name='core_user_profile'),

    url(r'^teams/add/$', view='preferences.organization_add', name='core_organization_add'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/(?P<id>[-\w]+)/delete/$', view='preferences.organization_parameter_delete', name='core_organization_parameter_delete'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/(?P<id>[-\w]+)/$', view='preferences.organization_parameter_detail', name='core_organization_parameter_detail'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/list/(?P<list_id>[-\w]+)/$', view='preferences.organization_parameter_list', name='core_organization_parameter_list'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/$', view='preferences.organization_parameter', name='core_organization_parameter'),
    url(r'^teams/(?P<slug>[-\w]+)/activity/$', view='preferences.organitazion_activity', name='core_organization_activity'),
    url(r'^teams/', include('organizations.urls')),

    url(r'^invitations/', include(invitation_backend().get_urls())),

    url(r'^chooseorg/$', view='chooseorg'),
    url(r'^login/$', view='user_login', name='auth_login'),
    url(r'^logout/$', view='user_logout', name='auth_logout'),
    url(r'^orgswitcher/(?P<slug>[-\w]+)/$', view='orgswitcher'),
    url(r'^$', view='index', name='core_index'),
)
