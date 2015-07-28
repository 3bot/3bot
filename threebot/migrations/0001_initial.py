# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_type', models.CharField(default=b'string', max_length=20, choices=[(b'string', b'String'), (b'email', b'Email'), (b'bool', b'Boolean')])),
                ('name', models.CharField(max_length=255, verbose_name=b'identifier')),
                ('value', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ParameterList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(help_text=b'Parameter List owner', to='organizations.Organization')),
            ],
            options={
                'ordering': ['title', 'date_created'],
                'verbose_name': 'Parameter List',
                'verbose_name_plural': 'Parameter Lists',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unique_identifier', models.CharField(help_text=b'Unique Identifier to group multiple Task Versions', max_length=255, null=True, blank=True)),
                ('version_major', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('version_minor', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('is_readonly', models.BooleanField(default=False, help_text=b'Only Team-Admins can edit')),
                ('is_builtin', models.BooleanField(default=False, help_text=b'Will be executed as Python Module on 3bot Platform')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('desc', models.TextField(null=True, blank=True)),
                ('template', models.TextField(default=b'#!/bin/sh\n', help_text=b'To declare an input, type: {{ <data type>.<identifier> }}')),
                ('inputs_fingerprint', models.CharField(max_length=32, null=True, blank=True)),
                ('changelog', models.TextField(null=True, blank=True)),
                ('owner', models.ForeignKey(help_text=b'Task owner', to='organizations.Organization')),
            ],
            options={
                'ordering': ['owner', 'title'],
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
            },
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('ip', models.IPAddressField(verbose_name=b'IP-Address')),
                ('addr', models.CharField(help_text=b'For now we use the IP to connect to the worker', max_length=200, null=True, blank=True)),
                ('port', models.PositiveIntegerField(default=55555)),
                ('secret_key', models.CharField(help_text=b'The Secret Key. Never share yours.', max_length=200, null=True, blank=True)),
                ('muted', models.BooleanField(default=False, help_text=b'Mute a Worker to prevent accessibility checks and improve performance.')),
                ('pre_task', models.TextField(help_text=b'this will run as a Script before the worker performs a workflow', null=True, blank=True)),
                ('post_task', models.TextField(help_text=b'this will run as a Script after the worker has performed a workflow', null=True, blank=True)),
                ('owner', models.ForeignKey(help_text=b'Worker owner', to='organizations.Organization')),
            ],
            options={
                'ordering': ['owner', 'title'],
                'verbose_name': 'Worker',
                'verbose_name_plural': 'Workers',
            },
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unique_identifier', models.CharField(help_text=b'Unique Identifier to group multiple Workflow Versions', max_length=255, null=True, blank=True)),
                ('version_major', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('version_minor', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('desc', models.TextField(null=True, blank=True)),
                ('pre_task', models.TextField(help_text=b'This will run as a Script before the worker runs a task of the current workflow. (Runs before each task)', null=True, blank=True)),
                ('post_task', models.TextField(help_text=b'This will run as a Script after the worker has executed a task of the current workflow. (Runs after each task)', null=True, blank=True)),
                ('owner', models.ForeignKey(help_text=b'Workflow owner', to='organizations.Organization')),
            ],
            options={
                'ordering': ['owner', 'title'],
                'verbose_name': 'Workflow',
                'verbose_name_plural': 'Workflows',
            },
        ),
        migrations.CreateModel(
            name='WorkflowLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(help_text=b'Date the workflow was performed', auto_now_add=True)),
                ('exit_code', models.PositiveIntegerField(default=2, choices=[(0, b'Success'), (1, b'Error'), (2, b'Pending')])),
                ('inputs', jsonfield.fields.JSONField()),
                ('outputs', jsonfield.fields.JSONField(null=True, blank=True)),
                ('performed_by', models.ForeignKey(help_text=b'The User who performed the Worfkflow', to=settings.AUTH_USER_MODEL)),
                ('performed_on', models.ForeignKey(help_text=b'The Worker Worfkflow was performed on', to='threebot.Worker')),
                ('workflow', models.ForeignKey(verbose_name='Workflow', to='threebot.Workflow')),
            ],
            options={
                'ordering': ['-date_created'],
                'verbose_name': 'Workflow Log',
                'verbose_name_plural': 'Workflow Logs',
            },
        ),
        migrations.CreateModel(
            name='WorkflowPreset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('defaults', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
                ('user', models.ForeignKey(verbose_name=b'User', to=settings.AUTH_USER_MODEL)),
                ('workflow', models.ForeignKey(verbose_name='Workflow', to='threebot.Workflow')),
            ],
            options={
                'ordering': ['date_modified', 'workflow', 'user'],
                'verbose_name': 'Workflow Preset',
                'verbose_name_plural': 'Workflow Presets',
            },
        ),
        migrations.CreateModel(
            name='WorkflowTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('next_workflow_task', models.ForeignKey(related_name='next_wt', on_delete=django.db.models.deletion.SET_NULL, verbose_name='The next Workflow Task', blank=True, to='threebot.WorkflowTask', null=True)),
                ('prev_workflow_task', models.ForeignKey(related_name='prev_wt', on_delete=django.db.models.deletion.SET_NULL, verbose_name='The previous Workflow Task', blank=True, to='threebot.WorkflowTask', null=True)),
                ('task', models.ForeignKey(verbose_name='Task', to='threebot.Task')),
                ('workflow', models.ForeignKey(verbose_name='Workflow', to='threebot.Workflow')),
            ],
            options={
                'ordering': ['workflow', 'task'],
                'verbose_name': 'Workflow Task',
                'verbose_name_plural': 'Workflow Tasks',
            },
        ),
        migrations.CreateModel(
            name='OrganizationParameter',
            fields=[
                ('parameter_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='threebot.Parameter')),
                ('owner', models.ForeignKey(help_text=b'Parameter owner', to='organizations.Organization')),
            ],
            options={
                'ordering': ['owner', 'data_type'],
                'verbose_name': 'Parameter for Team',
                'verbose_name_plural': 'Parameters for Team',
            },
            bases=('threebot.parameter',),
        ),
        migrations.CreateModel(
            name='UserParameter',
            fields=[
                ('parameter_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='threebot.Parameter')),
                ('owner', models.ForeignKey(help_text=b'Parameter owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['owner', 'data_type'],
                'verbose_name': 'Parameter for User',
                'verbose_name_plural': 'Parameters for Users',
            },
            bases=('threebot.parameter',),
        ),
        migrations.AddField(
            model_name='workflow',
            name='tasks',
            field=models.ManyToManyField(to='threebot.Task', through='threebot.WorkflowTask'),
        ),
        migrations.AlterUniqueTogether(
            name='workflowpreset',
            unique_together=set([('workflow', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='workflow',
            unique_together=set([('unique_identifier', 'version_major', 'version_minor')]),
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([('unique_identifier', 'version_major', 'version_minor')]),
        ),
        migrations.AddField(
            model_name='parameterlist',
            name='parameters',
            field=models.ManyToManyField(help_text=b'Select Parameters for this Team.', related_name='lists', to='threebot.OrganizationParameter'),
        ),
    ]
