from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from cloudinary_storage.storage import MediaCloudinaryStorage
from cloudinary.models import CloudinaryField
from ckeditor_uploader.fields import RichTextUploadingField
from cloudinary.api import resource
from django.utils.timezone import now 

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email

class ContactSender(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(blank=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional field for phone number
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)

    def __str__(self):
        return self.name
        
class User(AbstractUser):
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    is_member = models.BooleanField(default=False)
    is_officer = models.BooleanField(default=False)
    profile_picture = CloudinaryField('profile_pics', blank=True, null=True) # Optional field for profile picture
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional field for phone number
    birthdate = models.DateField(null=True, blank=True)  # Optional field for birthdate
    email = models.EmailField(unique=True)
    proof_of_membership =  CloudinaryField('membership_proof')

    class Meta:
        app_label = 'SVG2'
    
    def is_user_officer(self):
        """Returns True if the user is an officer, False otherwise."""
        return self.is_officer
    
    def is_user_member(self):
        """Returns True if the user is an officer, False otherwise."""
        return self.is_member

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True, related_name='member_profile')

class Officer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True, related_name='officer_profile')
    ROLES_CHOICES = (
        ('President', 'President'),
        ('Vice President', 'Vice President'),
        ('Secretary', 'Secretary'),
        ('Treasurer', 'Treasurer'),
        ('Auditor', 'Auditor'),
        ('P.R.O.', 'P.R.O.'),
        ('Grievance & Adjudication', 'Grievance & Adjudication'),
        ('Business & Finance', 'Business & Finance'),
        ('Peace & Order', 'Peace & Order'),
        ('Sports Committee', 'Sports Committee'),
        ('Seniors Affair', 'Seniors Affair'),
    )
    officer_position = models.CharField(max_length=50, choices=ROLES_CHOICES)

class Household(models.Model):
    BLOCK_CHOICES = (
    ('2','2'),
    ('3','3'),
    ('4','4'),
    ('5','5'),
    ('6','6'),
    ('7','7'),
    ('8','8'),
    ('10','10'),
    )

    STREET_CHOICES = (
        ('Bellflower', 'Bellflower'),
        ('Carnation', 'Carnation'),
        ('Dahlia', 'Dahlia'),
        ('Daisy', 'Daisy'),
        ('Gardenia', 'Gardenia'),
        ('Hyacinth', 'Hyacinth'),
        ('Petunia', 'Petunia'),
        ('Poinsettia', 'Poinsettia'),
        ('Primrose', 'Primrose'),
    )

    HOME_TENURE_CHOICES = (
        ('Owner', 'Owner'),
        ('Renter', 'Renter'),
        ('Caretaker', 'Caretaker'),
    )

    LAND_TENURE_CHOICES = (
        ('Owner', 'Owner'),
        ('Occupant', 'Occupant'),
        ('Settler', 'Settler'),
    )

    CONSTRUCTION_CHOICES = (
        ('Concrete', 'Concrete'),
        ('Half Concrete', 'Half Concrete'),
        ('Nipa', 'Nipa'),
        ('Wood', 'Wood'),
    )

    KITCHEN_CHOICES = (
        ('Shared', 'Shared'),
        ('Separate', 'Separate'),
    )

    WATER_FACILITY_CHOICES = (
        ('Pump', 'Pump'),
        ('Deepwell', 'Deepwell'),
        ('Primewater', 'Primewater'),
    )

    TOILET_FACILITY_CHOICES = (
        ('None', 'None'),
        ('Open Pit Owned', 'Open Pit Owned'),
        ('Open Pit Shared', 'Open Pit Shared'),
        ('Close Pit Owned', 'Close Pit Owned'),
        ('Close Pit Shared', 'Close Pit Shared'),
        ('Water Sealed Owned', 'Water Sealed Owned'),
        ('Water Sealed Shared', 'Water Sealed Shared'),
    )
    
    owner_name = models.OneToOneField(User, on_delete=models.CASCADE, related_name='household')
    block = models.CharField(max_length=50, choices=BLOCK_CHOICES)
    lot = models.CharField(max_length=50)
    street = models.CharField(max_length=10, choices=STREET_CHOICES)
    home_tenure = models.CharField(max_length=10, choices=HOME_TENURE_CHOICES)
    land_tenure = models.CharField(max_length=10, choices=LAND_TENURE_CHOICES)
    construction = models.CharField(max_length=13, choices=CONSTRUCTION_CHOICES)
    vehicles_owned = models.JSONField(blank=True, null=True)
    kitchen = models.CharField(max_length=10, choices=KITCHEN_CHOICES)
    water_facility = models.CharField(max_length=10, choices=WATER_FACILITY_CHOICES)
    toilet_facility = models.CharField(max_length=19, choices=TOILET_FACILITY_CHOICES)
    details_changed_by_officer = models.BooleanField(default=False)

    def number_of_residents(self):
        # Ensure there's always at least 1 (the owner) counted as a resident
        return max(0, self.residents.count())
    
    def total_vehicles(self):
        """Calculate the total number of vehicles."""
        return sum(self.vehicles_owned.values())

    def __str__(self):
         return f"{self.owner_name.fname} {self.owner_name.lname}"
         
class Resident(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    CIVIL_STATUS_CHOICES = (
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated'),
        ('Divorced', 'Divorced'),
    )
    EDUCATIONAL_ATTAINMENT_CHOICES = (
        ('None', 'None'),
        ('Elementary', 'Elementary'),
        ('High School', 'High School'),
        ('College', 'College'),
        ('Vocational', 'Vocational'),
        ('Masters', 'Masters'),
        ('Doctorate', 'Doctorate'),
    )
    RELIGION_CHOICES = (
        ('Roman Catholic', 'Roman Catholic'),
        ('Christianity', 'Christianity'),
        ('Islam', 'Islam'),
        ('Non-Religious', 'Non-Religious'),
    )

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='residents')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birthdate = models.DateField(null=True, blank=True)
    is_head_of_family = models.BooleanField(default=False)
    relation_to_head = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    contact_number = models.CharField(max_length=15)
    civil_status = models.CharField(max_length=10, choices=CIVIL_STATUS_CHOICES)
    religion = models.CharField(max_length=50, choices=RELIGION_CHOICES)
    educational_attainment = models.CharField(max_length=50, choices=EDUCATIONAL_ATTAINMENT_CHOICES)
    details_changed_by_officer = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Reservation(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateField()
    reservation_time_start = models.TimeField()
    reservation_time_end = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    AMENITY_CHOICES = (
        ('Court', 'Court'),
        ('Chairs & Tables', 'Chairs & Tables'),
        ('Event Hall', 'Event Hall'),
    )
    amenities = models.CharField(max_length=100, choices=AMENITY_CHOICES, default='Court')
    message = models.TextField(blank=True)
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Denied', 'Denied'),
        ('Canceled', 'Canceled'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    status_changed_by_officer = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.household} - {self.reservation_date} at {self.reservation_time_start}"
    
    @classmethod
    def confirmed_reservations(cls):
        # Return only confirmed events
        return cls.objects.filter(status='Confirmed')
    
    @classmethod
    def cancel_expired_reservations(cls):
        # Get current date and time
        now = timezone.now().date()

        # Find all pending reservations where the date has passed
        expired_reservations = cls.objects.filter(status='Pending', reservation_date__lt=now)

        # Update the status to 'Canceled' for expired reservations
        expired_reservations.update(status='Canceled')

        return expired_reservations
    
class ServiceRequest(models.Model):
    SERVICE_CHOICES = (
        ('Maintenance Request', 'Maintenance Request'),
        ('Incident Report', 'Incident Report'),
    )
    REQUEST_STATUS_CHOICES = (
        ('Submitted', 'Submitted'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
    )
    STREET_CHOICES = (
        ('Bellflower', 'Bellflower'),
        ('Carnation', 'Carnation'),
        ('Dahlia', 'Dahlia'),
        ('Daisy', 'Daisy'),
        ('Gardenia', 'Gardenia'),
        ('Hyacinth', 'Hyacinth'),
        ('Petunia', 'Petunia'),
        ('Poinsettia', 'Poinsettia'),
        ('Primrose', 'Primrose'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='Maintenance Request')
    street = models.CharField(max_length=10, choices=STREET_CHOICES)
    image = CloudinaryField('service_requests', blank=True, null=True)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='service_requests')
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='Submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.household.owner_name.fname} {self.household.owner_name.lname}- {self.get_service_type}: {self.title}"

class Billing(models.Model):
    STATUS_CHOICES = (
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
    )

    household = models.ForeignKey('Household', on_delete=models.CASCADE, related_name='billings')
    billing_month = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default='280')
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default='Unpaid')
    # Any other fields you think are necessary

    def __str__(self):
        return f'{self.household} - {self.billing_month.strftime("%B %Y")}'

    class Meta:
        ordering = ['-billing_month']
        unique_together = ('household', 'billing_month')  # Ensure one billing entry per household per month

class Newsfeed(models.Model):
    written_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='news_notices')
    title = models.CharField(max_length=255)
    description = RichTextUploadingField(config_name='default') 
    image = CloudinaryField('news', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.written_by.officer_profile.officer_position} - {self.title} - {self.created_at}'
    
class Announcement(models.Model):
    who = models.CharField(max_length=200)
    what = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    where = models.CharField(max_length=200)
    image = CloudinaryField('announcements', null=True, blank=True)

    def __str__(self):
        return f"Announcement on {self.date} at {self.time}"

class GrievanceAppointment(models.Model):
    APPOINTMENT_CHOICES = (
        ('Certification', 'Certification'),
        ('Grievance', 'Grievance'),
        ('Others', 'Others'),
    )
    PURPOSE_CHOICES = (
        ('Homeowners Certificate', 'Homeowners Certificate'),
        ('Move In / Move Out', 'Move In / Move Out'),
        ('Gate Pass', 'Gate Pass'),
        ('Business Permit (New/Renewal)', 'Business Permit (New/Renewal)'),
        ('Building Permit (Renovation/Extension/Fence)', 'Building Permit (Renovation/Extension/Fence)'),
        ('Employment/Loan/School/Police Clearance/ID', 'Employment/Loan/School/Police Clearance/ID'),
        ('Car Sticker', 'Car Sticker'),
        ('Other', 'Other Purpose (Specify)'),
    )
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='grievance_appointments')
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_CHOICES, default='Certification')
    subject = models.CharField(max_length=255)
    reservation_date = models.DateField()
    description = models.TextField(blank=True)
    image = CloudinaryField('appointments', blank=True, null=True)  # Ensure you have Pillow installed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Denied', 'Denied'),
        ('Canceled', 'Canceled'),
        ('Rescheduled', 'Rescheduled'),
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    status_changed_by_officer = models.BooleanField(default=False)
    certification_details = models.JSONField(blank=True, null=True)  # To store the additional fields for certification
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, blank=True, null=True)
    certification_pdf_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.household} - {self.reservation_date}"

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20]  # Show first 20 characters of the not

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)  # Link directly to officer
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    related_model = models.CharField(max_length=50, null=True, blank=True)
    related_id = models.IntegerField(null=True, blank=True)

    class Meta:
        # Indexing `created_at` for faster ordering
        indexes = [
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at'] 
        
    def __str__(self):
        return f"Notification for {self.recipient} - {self.content}"

class FinancialFile(models.Model):
    title = models.CharField(max_length=255)
    file = CloudinaryField('file')  # CloudinaryField to store the file
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def file_size(self):
        if self.file:
            # Get the Cloudinary file resource metadata
            file_info = resource(self.file.public_id)
            size = file_info.get('bytes', 0)  # 'bytes' contains the file size in bytes

            # Convert the file size to a readable format
            for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
        return "0 bytes"

    def __str__(self):
        return self.title

class Term(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title

class EmergencyHotline(models.Model):
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} - {self.number}"

class ElectionSession(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_open = models.BooleanField(default=False)  # New field to toggle election status manually

    def __str__(self):
        return self.name

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidacy')
    election = models.ForeignKey(ElectionSession, on_delete=models.CASCADE, related_name='candidates')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    election = models.ForeignKey(ElectionSession, on_delete=models.CASCADE, related_name='votes')
    candidates = models.ManyToManyField(Candidate, related_name='votes')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vote by {self.voter.username} in {self.election.name}"