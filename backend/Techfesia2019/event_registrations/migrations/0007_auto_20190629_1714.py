# Generated by Django 2.2.2 on 2019-06-29 11:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event_registrations', '0006_auto_20190628_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='member_teams', to='accounts.Profile'),
        ),
    ]
