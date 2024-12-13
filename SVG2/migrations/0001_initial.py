# Generated by Django 5.1.4 on 2024-12-13 02:20

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('who', models.CharField(max_length=200)),
                ('what', models.TextField()),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('where', models.CharField(max_length=200)),
                ('image', models.ImageField(blank=True, null=True, upload_to='announcements_images/')),
            ],
        ),
        migrations.CreateModel(
            name='ContactSender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Household',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block', models.CharField(choices=[('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('10', '10')], max_length=50)),
                ('lot', models.CharField(max_length=50)),
                ('street', models.CharField(choices=[('Bellflower', 'Bellflower'), ('Carnation', 'Carnation'), ('Dahlia', 'Dahlia'), ('Daisy', 'Daisy'), ('Gardenia', 'Gardenia'), ('Hyacinth', 'Hyacinth'), ('Petunia', 'Petunia'), ('Poinsettia', 'Poinsettia'), ('Primrose', 'Primrose')], max_length=10)),
                ('home_tenure', models.CharField(choices=[('Owner', 'Owner'), ('Renter', 'Renter'), ('Caretaker', 'Caretaker')], max_length=10)),
                ('land_tenure', models.CharField(choices=[('Owner', 'Owner'), ('Occupant', 'Occupant'), ('Settler', 'Settler')], max_length=10)),
                ('construction', models.CharField(choices=[('Concrete', 'Concrete'), ('Half Concrete', 'Half Concrete'), ('Nipa', 'Nipa'), ('Wood', 'Wood')], max_length=13)),
                ('vehicles_owned', models.TextField(blank=True, null=True)),
                ('kitchen', models.CharField(choices=[('Shared', 'Shared'), ('Separate', 'Separate')], max_length=10)),
                ('water_facility', models.CharField(choices=[('Pump', 'Pump'), ('Deepwell', 'Deepwell'), ('Primewater', 'Primewater')], max_length=10)),
                ('toilet_facility', models.CharField(choices=[('None', 'None'), ('Open Pit Owned', 'Open Pit Owned'), ('Open Pit Shared', 'Open Pit Shared'), ('Close Pit Owned', 'Close Pit Owned'), ('Close Pit Shared', 'Close Pit Shared'), ('Water Sealed Owned', 'Water Sealed Owned'), ('Water Sealed Shared', 'Water Sealed Shared')], max_length=19)),
                ('details_changed_by_officer', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('fname', models.CharField(max_length=30)),
                ('lname', models.CharField(max_length=30)),
                ('is_member', models.BooleanField(default=False)),
                ('is_officer', models.BooleanField(default=False)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='C:/HOA_MIS/media/profile_pics/')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GrievanceAppointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_type', models.CharField(choices=[('Certification', 'Certification'), ('Grievance', 'Grievance'), ('Others', 'Others')], default='Certification', max_length=20)),
                ('subject', models.CharField(max_length=255)),
                ('reservation_date', models.DateField()),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='C:/HOA_MIS/media/news_notices')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Denied', 'Denied'), ('Canceled', 'Canceled'), ('Rescheduled', 'Rescheduled')], default='Pending', max_length=15)),
                ('status_changed_by_officer', models.BooleanField(default=False)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grievance_appointments', to='SVG2.household')),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='member_profile', serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Officer',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='officer_profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('officer_position', models.CharField(choices=[('President', 'President'), ('Vice President', 'Vice President'), ('Secretary', 'Secretary'), ('Treasurer', 'Treasurer'), ('Auditor', 'Auditor'), ('P.R.O.', 'P.R.O.'), ('Grievance & Adjudication', 'Grievance & Adjudication'), ('Business & Finance', 'Business & Finance'), ('Peace & Order', 'Peace & Order'), ('Sports Committee', 'Sports Committee'), ('Seniors Affair', 'Seniors Affair')], max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='household',
            name='owner_name',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='household', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Newsfeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='C:/HOA_MIS/media/news_notices')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('written_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news_notices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reservation_date', models.DateField()),
                ('reservation_time_start', models.TimeField()),
                ('reservation_time_end', models.TimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amenities', models.CharField(choices=[('Court', 'Court'), ('Chairs & Tables', 'Chairs & Tables'), ('Event Hall', 'Event Hall')], default='Court', max_length=100)),
                ('message', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Denied', 'Denied'), ('Canceled', 'Canceled')], default='Pending', max_length=10)),
                ('status_changed_by_officer', models.BooleanField(default=False)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='SVG2.household')),
            ],
        ),
        migrations.CreateModel(
            name='Resident',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('suffix', models.CharField(blank=True, max_length=10)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('is_head_of_family', models.BooleanField(default=False)),
                ('relation_to_head', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('contact_number', models.CharField(max_length=15)),
                ('civil_status', models.CharField(choices=[('Single', 'Single'), ('Married', 'Married'), ('Widowed', 'Widowed'), ('Separated', 'Separated'), ('Divorced', 'Divorced')], max_length=10)),
                ('religion', models.CharField(choices=[('Roman Catholic', 'Roman Catholic'), ('Christianity', 'Christianity'), ('Islam', 'Islam'), ('Non-Religious', 'Non-Religious')], max_length=50)),
                ('educational_attainment', models.CharField(choices=[('None', 'None'), ('Elementary', 'Elementary'), ('High School', 'High School'), ('College', 'College'), ('Vocational', 'Vocational'), ('Masters', 'Masters'), ('Doctorate', 'Doctorate')], max_length=50)),
                ('details_changed_by_officer', models.BooleanField(default=False)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='residents', to='SVG2.household')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('service_type', models.CharField(choices=[('Maintenance Request', 'Maintenance Request'), ('Incident Report', 'Incident Report')], default='Maintenance Request', max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='service_requests/')),
                ('status', models.CharField(choices=[('Submitted', 'Submitted'), ('In Progress', 'In Progress'), ('Completed', 'Completed'), ('Canceled', 'Canceled')], default='Submitted', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status_changed_by_officer', models.BooleanField(default=False)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to='SVG2.household')),
            ],
        ),
        migrations.CreateModel(
            name='Billing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_month', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, default='280', max_digits=10)),
                ('status', models.CharField(choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid'), ('Overdue', 'Overdue')], default='Unpaid', max_length=7)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billings', to='SVG2.household')),
            ],
            options={
                'ordering': ['-billing_month'],
                'unique_together': {('household', 'billing_month')},
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('read', models.BooleanField(default=False)),
                ('related_model', models.CharField(blank=True, max_length=50, null=True)),
                ('related_id', models.IntegerField(blank=True, null=True)),
                ('recipient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['created_at'], name='SVG2_notifi_created_cb8278_idx')],
            },
        ),
    ]
