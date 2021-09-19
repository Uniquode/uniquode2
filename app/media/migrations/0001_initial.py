# Generated by Django 3.2.7 on 2021-09-19 04:26

from django.db import migrations, models
import django.db.models.manager
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='Icon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Icon Name')),
                ('svg', models.TextField(verbose_name='SVG')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'ordering': ['name'],
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('_related', django.db.models.manager.Manager()),
            ],
        ),
    ]