# Generated by Django 5.1.4 on 2025-01-25 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0019_electionsession_candidate_vote'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='electionsession',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='electionsession',
            name='end_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='electionsession',
            name='start_date',
            field=models.DateTimeField(),
        ),
    ]