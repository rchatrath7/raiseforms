# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-11 00:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('forms', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abstractusermodel',
            name='tagline',
        ),
        migrations.AddField(
            model_name='abstractusermodel',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='abstractusermodel',
            name='is_active',
            field=models.BooleanField(default=False, editable=False, verbose_name='Active'),
        ),
        migrations.AddField(
            model_name='abstractusermodel',
            name='is_staff',
            field=models.BooleanField(default=False, editable=False, verbose_name='Staff'),
        ),
        migrations.AddField(
            model_name='abstractusermodel',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status'),
        ),
        migrations.AddField(
            model_name='abstractusermodel',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterField(
            model_name='abstractusermodel',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Admin'),
        ),
    ]