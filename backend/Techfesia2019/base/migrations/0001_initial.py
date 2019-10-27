# Generated by Django 2.2.2 on 2019-10-27 18:12

import base.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileUploadModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purpose', models.CharField(max_length=100)),
                ('upload_path', models.CharField(max_length=250)),
                ('forced_filename', models.CharField(blank=True, max_length=80, null=True)),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
                ('uploaded_file', models.FileField(upload_to=base.models.set_file_upload_path)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImageUploadModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purpose', models.CharField(max_length=100)),
                ('upload_path', models.CharField(max_length=250)),
                ('forced_filename', models.CharField(blank=True, max_length=80, null=True)),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
                ('uploaded_image', models.ImageField(upload_to=base.models.set_file_upload_path)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
