# Generated by Django 2.2.2 on 2019-06-27 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event_registrations', '0003_auto_20190627_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teameventregistration',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='event_registrations.Team'),
        ),
    ]
