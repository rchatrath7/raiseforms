# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-09 04:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forms', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='email',
        ),
        migrations.RemoveField(
            model_name='client',
            name='name',
        ),
        migrations.RemoveField(
            model_name='executive',
            name='email',
        ),
        migrations.RemoveField(
            model_name='executive',
            name='name',
        ),
        migrations.RemoveField(
            model_name='executive',
            name='username',
        ),
        migrations.AddField(
            model_name='client',
            name='user',
            field=models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='executive',
            name='user',
            field=models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]