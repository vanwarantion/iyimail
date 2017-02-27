# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-27 02:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iyimail', '0002_email_recipient'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('subject', models.CharField(default='', max_length=989, verbose_name='Subject')),
                ('message', models.TextField(default='', verbose_name='Message')),
                ('html_message', models.TextField(default='', verbose_name='HTML Message')),
            ],
        ),
    ]
