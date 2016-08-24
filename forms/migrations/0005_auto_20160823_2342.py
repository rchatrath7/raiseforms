# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-24 03:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0004_abstractusermodel__is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abstractusermodel',
            name='token',
        ),
        migrations.AddField(
            model_name='client',
            name='consulting_agreement_token',
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='nda_token',
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='statement_of_work_token',
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='token',
            field=models.CharField(max_length=16, null=True),
        ),
    ]
