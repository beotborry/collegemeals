# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-25 00:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0002_auto_20170924_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='type',
            field=models.CharField(blank=True, choices=[('BR', 'breakfast'), ('LU', 'lunch'), ('DN', 'dinner')], max_length=2),
        ),
    ]
