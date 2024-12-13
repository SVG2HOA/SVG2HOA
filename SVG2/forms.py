from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Member, Officer, Household, Resident, Reservation, ServiceRequest, Billing, Newsfeed, NewsletterSubscriber, ContactSender, Announcement, GrievanceAppointment, Note, Notification
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import datetime, date, time
from django.contrib.auth import authenticate


User = get_user_model()

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSender
        fields = ['name', 'email', 'phone_number', 'title', 'message']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username", 
        max_length=254, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        label="Password", 
        strip=False, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    remember_me = forms.BooleanField(label="Remember me", required=False)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Step 1: Check if the user exists and if they are active
            try:
                user = User.objects.get(username=username)
                # Step 2: If user is inactive, raise validation error
                if not user.is_active:
                    raise forms.ValidationError(
                        "Your account is inactive. Please contact an officer.",
                        code='inactive_account',
                    )
            except User.DoesNotExist:
                # If the user does not exist, raise a validation error for incorrect username
                raise forms.ValidationError(
                    "Username does not exist.",
                    code='username_not_found',
                )

            # Step 3: Authenticate the user using the password
            user = authenticate(username=username, password=password)

            # Step 4: If authentication fails, raise the incorrect password error
            if user is None:
                raise forms.ValidationError(
                    "Incorrect password.",
                    code='incorrect_password',
                )

            # If authentication is successful, cache the user
            self.user_cache = user
        else:
            # If either username or password is missing, raise validation error
            raise forms.ValidationError(
                "Both username and password are required.",
                code='missing_fields',
            )

        return self.cleaned_data

    def get_user(self):
        # Return the cached user if authentication passed
        return getattr(self, 'user_cache', None)

class UserSignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}))
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control","placeholder": "Email"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"}))
    user_type = forms.ChoiceField(
        choices=[('member', 'Member'), ('officer', 'Officer')],
        widget=forms.Select(attrs={"class": "form-control", "placeholder": "User Type"})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password1')
        confirm_password = cleaned_data.get('password2')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        # Check if the email is already taken
        email = cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        user_type = self.cleaned_data['user_type']

        # Set the user type flags
        if user_type == 'member':
            user.is_member = True
        elif user_type == 'officer':
            user.is_officer = True

        user.is_active = False  # Default inactive for all new users
        if commit:
            user.save()

            # Create corresponding profile
            if user.is_member:
                Member.objects.create(user=user)
            elif user.is_officer:
                Officer.objects.create(user=user)

        return user

class MemberChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['fname', 'lname', 'username', 'email', 'profile_picture', 'phone_number', 'birthdate']

class OfficerChangeForm(forms.ModelForm):
    officer_position = forms.ChoiceField(choices=Officer.ROLES_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['profile_picture', 'fname', 'lname', 'username', 'email', 'phone_number', 'birthdate', 'officer_position']

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.pop('instance', None)
        super(OfficerChangeForm, self).__init__(*args, **kwargs, instance=user_instance)
        if user_instance:
            officer_instance = Officer.objects.filter(user=user_instance).first()
            if officer_instance:
                self.fields['officer_position'].initial = officer_instance.officer_position

    def save(self, commit=True):
        user = super(OfficerChangeForm, self).save(commit=commit)
        officer_position = self.cleaned_data.get('officer_position')
        Officer.objects.update_or_create(user=user, defaults={'officer_position': officer_position})
        return user

class RememberMeAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label='Remember_Me', initial=True)

class HouseholdForm(forms.ModelForm):
    VEHICLE_CHOICES = (
        ('Bicycle', 'Bicycle'),
        ('Motorcycle', 'Motorcycle'),
        ('Tricycle', 'Tricycle'),
        ('Car', 'Car'),
        ('Cab', 'Cab'),
        ('Van', 'Van'),
    )

    vehicles_owned = forms.MultipleChoiceField(choices=VEHICLE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = Household
        fields = ['block', 'lot', 'street', 'home_tenure', 'land_tenure', 'construction', 'kitchen', 'vehicles_owned', 'water_facility', 'toilet_facility']

    def __init__(self, *args, **kwargs):
        super(HouseholdForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.vehicles_owned:
            self.fields['vehicles_owned'].initial = self.instance.vehicles_owned.split(', ')

    def save(self, commit=True):
        instance = super(HouseholdForm, self).save(commit=False)
        instance.vehicles_owned = ', '.join(self.cleaned_data['vehicles_owned'])
        if commit:
            instance.save()
        return instance

class ResidentForm(forms.ModelForm):
    class Meta:
        model = Resident
        exclude = ('household',)
        fields = [
            'first_name', 'middle_name', 'last_name', 'suffix', 'gender', 
            'birthdate', 'is_head_of_family', 'relation_to_head', 'email', 
            'contact_number', 'civil_status', 'religion', 'educational_attainment'
        ]
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ResidentForm, self).__init__(*args, **kwargs)
        self.fields['relation_to_head'].required = False

    def clean(self):
        cleaned_data = super().clean()
        is_head_of_family = cleaned_data.get("is_head_of_family")
        relation_to_head = cleaned_data.get("relation_to_head")

        if is_head_of_family:
            cleaned_data["relation_to_head"] = "Head"
        elif not relation_to_head:
            self.add_error('relation_to_head', 'This field is required if not head of family.')

        return cleaned_data

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['amenities', 'reservation_date', 'reservation_time_start', 'reservation_time_end', 'message']
    
    def clean(self):
        cleaned_data = super().clean()
        reservation_date = cleaned_data.get("reservation_date")
        reservation_start = cleaned_data.get("reservation_time_start")
        reservation_end = cleaned_data.get("reservation_time_end")
        
        if reservation_date and reservation_date < date.today():
            raise ValidationError("Reservation date cannot be in the past.")
        
        if reservation_start and reservation_end and reservation_start >= reservation_end:
            raise ValidationError("Start time must be before end time.")
    
class ReservationStatusForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['status']

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['service_type', 'title', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class BillingStatusForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['status']

class NewsfeedForm(forms.ModelForm):
    class Meta:
        model = Newsfeed
        fields = ['title','description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class ServiceRequestStatusForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['status']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['who', 'what', 'date', 'time', 'where', 'image']

class GrievanceForm(forms.ModelForm):
    class Meta:
        model = GrievanceAppointment
        fields = ['appointment_type', 'subject', 'reservation_date', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_reservation_date(self):
        reservation_date = self.cleaned_data.get('reservation_date')
        if reservation_date and reservation_date.weekday() != 6:  # 6 represents Sunday
            raise ValidationError("Appointments are only available on Sundays.")
        return reservation_date

class GrievanceStatusForm(forms.ModelForm):
    class Meta:
        model = GrievanceAppointment
        fields = ['status', 'reservation_date']
    
    def clean_reservation_date(self):
        reservation_date = self.cleaned_data.get('reservation_date')
        if reservation_date and reservation_date.weekday() != 6:  # 6 represents Sunday
            raise ValidationError("Appointments are only available on Sundays.")
        return reservation_date

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter a reminder...'}),
        }