# Generated by Django 5.1.4 on 2025-01-14 05:56

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0007_alter_announcement_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='announcements'),
        ),
        migrations.AlterField(
            model_name='grievanceappointment',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='appointments'),
        ),
        migrations.AlterField(
            model_name='newsfeed',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='news'),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='service_requests'),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='profile_pics'),
        ),
    ]
