# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-03-01 00:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import iyimail.models


class Migration(migrations.Migration):

    dependencies = [
        ('iyimail', '0007_auto_20170227_2255'),
    ]

    operations = [
        migrations.CreateModel(
            name='Executions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='iyimail.Email')),
            ],
        ),
        migrations.AddField(
            model_name='ruletemplate',
            name='email_address_field',
            field=models.CharField(default='email', help_text='Field name that returns Email address of the recipient', max_length=500, verbose_name='Email Address Field'),
        ),
        migrations.AlterField(
            model_name='ruletemplate',
            name='context_method_name',
            field=models.CharField(help_text='Method name that returns context required by Email Template', max_length=500, verbose_name='Context Method Name'),
        ),
        migrations.AlterField(
            model_name='ruletemplate',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iyimail.EmailTemplate', verbose_name='Email Template'),
        ),
        migrations.AlterField(
            model_name='ruletemplate',
            name='trigger_age',
            field=models.CharField(blank=True, help_text='Timedelta based triggers only. Eg. Enter "days=3" for timedelta(days=3)', max_length=100, null=True, validators=[iyimail.models.validate_trigger_age], verbose_name='Trigger Age'),
        ),
        migrations.AlterField(
            model_name='ruletemplate',
            name='trigger_condition',
            field=models.CharField(blank=True, help_text='Overrides Trigger Age', max_length=500, null=True, verbose_name='Trigger Condition'),
        ),
        migrations.AlterField(
            model_name='ruletemplate',
            name='trigger_model',
            field=models.CharField(max_length=500, verbose_name='Trigger Model'),
        ),
        migrations.AlterField(
            model_name='ruletemplate',
            name='trigger_query_str',
            field=models.CharField(blank=True, help_text='Filter Argument', max_length=500, null=True, verbose_name='Model Argument'),
        ),
        migrations.AddField(
            model_name='executions',
            name='rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iyimail.RuleTemplate'),
        ),
    ]