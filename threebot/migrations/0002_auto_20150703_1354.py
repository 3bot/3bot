# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('threebot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowlog',
            name='date_finished',
            field=models.DateTimeField(help_text=b'Date the workflow was performed', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='workflowlog',
            name='date_started',
            field=models.DateTimeField(help_text=b'Date the workflow was performed', null=True, blank=True),
        ),
    ]
