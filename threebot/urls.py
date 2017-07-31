# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from organizations.backends import invitation_backend
from threebot.views.api import worker as api_views_worker
from threebot.views.api import log as api_views_log
from threebot.views import base as base_views
from threebot.views import preferences as preferences_views
from threebot.views import task as task_views
from threebot.views import worker as worker_views
from threebot.views import workflow as workflow_views


urlpatterns = [
    url(r'^worker/add/$', worker_views.create, name='core_worker_create'),
    url(r'^worker/(?P<slug>[-\w]+)/delete/$', worker_views.delete, name='core_worker_delete'),
    url(r'^worker/(?P<slug>[-\w]+)/manual/$', worker_views.detail_manual, name='core_worker_detail_manual'),
    url(r'^worker/(?P<slug>[-\w]+)/digest/$', worker_views.detail_digest, name='core_worker_detail_digest'),
    url(r'^worker/(?P<slug>[-\w]+)/$', worker_views.detail_edit, name='core_worker_detail'),
    url(r'^worker/$', worker_views.list, name='core_worker_list'),
    url(r'^wk/(?P<id>[-\w]+)/$', worker_views.worker_permalink, name='core_worker_permalink'),

    url(r'^task/add/$', task_views.create, name='core_task_create'),
    url(r'^task/import/$', task_views.import_task, name='core_task_import'),
    url(r'^task/clone/(?P<taskslug>[-\w]+)-(?P<teamslug>[-\w]+)/$', task_views.clone_for_team, name='core_task_clone'),
    url(r'^task/(?P<slug>[-\w]+)/new_workflow/$', task_views.create_workflow, name='core_task_create_workflow'),
    url(r'^task/(?P<slug>[-\w]+)/delete/$', task_views.delete, name='core_task_delete'),
    url(r'^task/(?P<slug>[-\w]+)/export/$', task_views.export, name='core_task_export'),
    url(r'^task/(?P<slug>[-\w]+)/digest/$', task_views.detail_digest, name='core_task_detail_digest'),
    url(r'^task/(?P<slug>[-\w]+)/$', task_views.detail_edit, name='core_task_detail'),
    url(r'^task/$', task_views.list, name='core_task_list'),
    url(r'^t/(?P<id>[-\w]+)/$', task_views.task_permalink, name='core_task_permalink'),

    url(r'^workflow/add/$', workflow_views.create, name='core_workflow_create'),
    url(r'^workflow/(?P<slug>[-\w]+)/log/(?P<id>[-\w]+)/render/$', workflow_views.log_detail_render, name='core_workflow_log_detail_render'),
    url(r'^workflow/(?P<slug>[-\w]+)/log/(?P<id>[-\w]+)/$', workflow_views.log_detail, name='core_workflow_log_detail'),
    url(r'^workflow/(?P<slug>[-\w]+)/log/(?P<id>[-\w]+)/replay/$', workflow_views.replay, name='core_workflow_replay'),
    url(r'^workflow/(?P<slug>[-\w]+)/delete/$', workflow_views.delete, name='core_workflow_delete'),
    url(r'^workflow/(?P<slug>[-\w]+)/digest/$', workflow_views.detail_digest, name='core_workflow_detail_digest'),
    url(r'^workflow/(?P<slug>[-\w]+)/reorder/$', workflow_views.detail_reorder, name='core_workflow_detail_reorder'),
    url(r'^workflow/(?P<slug>[-\w]+)/edit/$', workflow_views.detail_edit, name='core_workflow_detail_edit'),
    url(r'^workflow/(?P<slug>[-\w]+)/with-list/$', workflow_views.detail_perf_with_list, name='core_workflow_detail_with_list'),
    url(r'^workflow/(?P<slug>[-\w]+)/$', workflow_views.detail_perf, name='core_workflow_detail'),
    url(r'^workflow/$', workflow_views.list, name='core_workflow_list'),
    url(r'^wf/(?P<id>[-\w]+)/$', workflow_views.workflow_permalink, name='core_workflow_permalink'),
    url(r'^log/(?P<id>[-\w]+)/$', workflow_views.workflow_log_permalink, name='core_workflow_log_permalink'),

    url(r'^user/parameter/(?P<id>[-\w]+)/delete/$', preferences_views.user_parameter_delete, name='core_user_parameter_delete'),
    url(r'^user/parameter/(?P<id>[-\w]+)/$', preferences_views.user_parameter_detail, name='core_user_parameter_detail'),
    url(r'^user/parameter/$', preferences_views.user_parameter, name='core_user_parameter'),
    url(r'^user/activity/$', preferences_views.user_activity, name='core_user_activity'),
    url(r'^user/$', preferences_views.user_profile, name='core_user_profile'),

    url(r'^teams/add/$', preferences_views.organization_add, name='core_organization_add'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/(?P<id>[-\w]+)/delete/$', preferences_views.organization_parameter_delete, name='core_organization_parameter_delete'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/(?P<id>[-\w]+)/$', preferences_views.organization_parameter_detail, name='core_organization_parameter_detail'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/list/(?P<list_id>[-\w]+)/$', preferences_views.organization_parameter_list, name='core_organization_parameter_list'),
    url(r'^teams/(?P<slug>[-\w]+)/parameter/$', preferences_views.organization_parameter, name='core_organization_parameter'),
    url(r'^teams/(?P<slug>[-\w]+)/activity/$', preferences_views.organitazion_activity, name='core_organization_activity'),
    url(r'^teams/', include('organizations.urls')),

    url(r'^invitations/', include(invitation_backend().get_urls())),

    url(r'^chooseorg/$', base_views.chooseorg),
    url(r'^login/$', base_views.user_login, name='auth_login'),
    url(r'^logout/$', base_views.user_logout, name='auth_logout'),
    url(r'^orgswitcher/(?P<slug>[-\w]+)/$', base_views.orgswitcher),
    url(r'^$', base_views.index, name='core_index'),

    ### API ###
    url(r'^api/workers/(?P<id>[-\d]+)/$', api_views_worker.detail, name='api_worker_detail'),
    url(r'^api/logs/(?P<id>[-\d]+)/$', api_views_log.detail, name='api_log_detail'),
]
