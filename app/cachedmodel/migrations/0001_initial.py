# Generated by Django 3.2.7 on 2021-09-19 03:41

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CachedModelTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_label', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('app_label', 'model'),
                'unique_together': {('app_label', 'model')},
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('_related', django.db.models.manager.Manager()),
            ],
        ),
    ]
