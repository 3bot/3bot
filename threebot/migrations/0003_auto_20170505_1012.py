# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-05 10:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('threebot', '0002_auto_20150703_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='ip',
            field=models.GenericIPAddressField(verbose_name=b'IP-Address'),
        ),
    ]
