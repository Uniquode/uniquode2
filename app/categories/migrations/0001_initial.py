# Generated by Django 3.2.7 on 2021-09-19 04:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Category Name')),
                ('slug', models.SlugField(max_length=64, unique=True, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='CategoryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField(db_index=True, verbose_name='object ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories_categoryitem_items', to='categories.category')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories_categoryitem_categories', to='contenttypes.contenttype', verbose_name='content type')),
            ],
            options={
                'verbose_name': 'category item',
                'verbose_name_plural': 'category items',
            },
        ),
    ]
