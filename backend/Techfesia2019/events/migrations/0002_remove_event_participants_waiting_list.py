# Generated by Django 2.2.2 on 2019-06-26 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='participants_waiting_list',
        ),
    ]
