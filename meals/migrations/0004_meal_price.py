# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-25 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0003_auto_20170925_0946'),
    ]

    operations = [
        migrations.AddField(
            model_name='meal',
            name='price',
            field=models.TextField(default='1,00원'),
            preserve_default=False,
        ),
    ]
