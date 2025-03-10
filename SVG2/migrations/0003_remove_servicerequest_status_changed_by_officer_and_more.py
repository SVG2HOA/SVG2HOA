# Generated by Django 5.1.4 on 2025-01-10 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0002_alter_user_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicerequest',
            name='status_changed_by_officer',
        ),
        migrations.AlterField(
            model_name='grievanceappointment',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='appointments/'),
        ),
        migrations.AlterField(
            model_name='newsfeed',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='news_notices/'),
        ),
    ]
