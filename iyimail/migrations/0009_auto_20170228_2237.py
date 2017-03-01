# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-03-01 06:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iyimail', '0008_auto_20170228_1644'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Executions',
            new_name='ExecutionLog',
        ),
        migrations.AlterModelOptions(
            name='emailtemplate',
            options={'verbose_name': 'Template'},
        ),
        migrations.AlterModelOptions(
            name='ruletemplate',
            options={'verbose_name': 'Rule'},
        ),
        migrations.AlterField(
            model_name='ruletemplate',
            name='email_address_field',
            field=models.CharField(default='email', help_text='Field name that returns Email address of the recipient.', max_length=500, verbose_name='Email Address Field'),
        ),
    ]