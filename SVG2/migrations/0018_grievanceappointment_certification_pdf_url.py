# Generated by Django 5.1.4 on 2025-01-24 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0017_grievanceappointment_purpose'),
    ]

    operations = [
        migrations.AddField(
            model_name='grievanceappointment',
            name='certification_pdf_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
