# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 07:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=512)),
                ('by', models.IntegerField(max_length=1)),
                ('ip', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grp_id', models.CharField(max_length=512)),
                ('company', models.CharField(max_length=512)),
                ('group_name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='IPMan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=512)),
                ('name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=512)),
                ('access_token', models.CharField(max_length=512)),
                ('grp', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='flockApp2.Group')),
            ],
        ),
        migrations.AddField(
            model_name='chat',
            name='grp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flockApp2.Group'),
        ),
        migrations.AddField(
            model_name='chat',
            name='ipman',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flockApp2.IPMan'),
        ),
    ]
