# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-07 02:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0007_auto_20160904_2112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nda',
            name='corporation',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='nda',
            name='location',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='nda',
            name='ssn',
            field=models.CharField(max_length=11, null=True),
        ),
        migrations.AlterField(
            model_name='nda',
            name='title',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='additional_notes',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='amount',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='contract_present',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='cost_center',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='invoice_cadence_recurring',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='payment_terms_net_30',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='payment_terms_receipt',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='purpose',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='recurring_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='service_period',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='vendor',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='additional_terms_of_services',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='agreement_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='deliverables',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='desc_of_services',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='fixed_pricing',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='fixed_rate',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='hourly_pricing',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='hourly_rate',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='milestone_pricing',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='milestone_rate',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='statementofwork',
            name='milestones',
            field=models.NullBooleanField(),
        ),
    ]
