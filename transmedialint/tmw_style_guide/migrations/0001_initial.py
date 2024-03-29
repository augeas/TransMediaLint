# Generated by Django 4.0.6 on 2022-07-25 01:33

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RatedArticle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offensive', models.IntegerField(default=0)),
                ('inaccurate', models.IntegerField(default=0)),
                ('inappropriate', models.IntegerField(default=0)),
                ('inappropriate_medical', models.IntegerField(default=0)),
                ('rating', models.CharField(choices=[('RED', 'red'), ('YEL', 'yellow'), ('GRN', 'green')], max_length=8)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sources.article')),
            ],
        ),
        migrations.CreateModel(
            name='AnnotatedSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0))),
                ('source', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sources.source')),
            ],
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=256)),
                ('tag', models.CharField(choices=[('OFF', 'offensive'), ('INAC', 'inaccurate'), ('INAP', 'inappropriate'), ('INAPMED', 'inappropriate_medical')], max_length=32)),
                ('label', models.CharField(max_length=64)),
                ('position', models.IntegerField()),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sources.article')),
            ],
            options={
                'unique_together': {('article', 'text', 'position')},
            },
        ),
    ]
