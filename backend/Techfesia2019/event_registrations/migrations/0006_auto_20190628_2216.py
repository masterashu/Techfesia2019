# Generated by Django 2.2.2 on 2019-06-28 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_registrations', '0005_auto_20190628_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='invitation_rejected',
            field=models.BooleanField(default=False, help_text="If true person has rejected invitation and can't accept it."),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='invitation_accepted',
            field=models.BooleanField(default=False, help_text='If true person has accepted invitation and is part of the team'),
        ),
    ]
