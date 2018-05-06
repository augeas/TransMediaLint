# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-27 03:57
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import sources.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('url', models.CharField(max_length=256, unique=True)),
                ('slug', models.SlugField(max_length=256)),
                ('date_published', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0))),
                ('date_retrieved', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0))),
                ('page', models.FileField(upload_to=sources.models.article_directory_path)),
                ('preview', models.FileField(upload_to=sources.models.preview_directory_path)),
                ('broken', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-date_published',),
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('slug', models.SlugField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('title', models.CharField(max_length=32, unique=True)),
                ('slug', models.SlugField(max_length=32)),
                ('last_scraped', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0))),
                ('region', models.CharField(max_length=32)),
                ('city', models.CharField(max_length=32)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='author',
            field=models.ManyToManyField(to='sources.Author'),
        ),
        migrations.AddField(
            model_name='article',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sources.Source'),
        ),
    ]
