# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-01 16:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('autenticacion', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductBacklog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=128)),
                ('fechaInicio', models.DateField()),
                ('fechaFinal', models.DateField()),
                ('developmentTeam', models.ManyToManyField(related_name='asdf3', to='autenticacion.User')),
                ('productBacklog', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='administracion.ProductBacklog')),
                ('productOwner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asdf2', to='autenticacion.User')),
                ('scrumMaster', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asdf', to='autenticacion.User')),
            ],
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sprint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administracion.Proyecto')),
            ],
        ),
        migrations.CreateModel(
            name='SprintBacklog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='proyecto',
            name='sprintBacklog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='administracion.SprintBacklog'),
        ),
    ]