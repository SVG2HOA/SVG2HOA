# Generated by Django 5.1.4 on 2025-01-24 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0015_servicerequest_street'),
    ]

    operations = [
        migrations.AddField(
            model_name='grievanceappointment',
            name='certification_details',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
