# Generated by Django 5.1.4 on 2025-01-24 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0011_alter_financialfile_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencyHotline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('number', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
    ]
