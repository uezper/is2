# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-23 22:30
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacion', '0007_auto_20160423_2223'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('users', django.db.models.manager.Manager()),
            ],
        ),
    ]
