from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.http import HttpResponse
import base64
import requests
import calendar as cal
from django.conf import settings
from django.http import HttpResponseRedirect
from collections import Counter
from datetime import date, timedelta, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import UserSignUpForm, ReservationForm, CustomLoginForm, HouseholdForm, ResidentForm, RememberMeAuthenticationForm, ReservationStatusForm, ServiceRequestForm, ServiceRequestStatusForm, BillingStatusForm, NewsfeedForm, NewsletterForm, OfficerChangeForm, MemberChangeForm, ContactForm, AnnouncementForm, GrievanceForm, GrievanceStatusForm, NoteForm, FinancialFileForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Household, Resident, Reservation, Billing, ServiceRequest, Newsfeed, Officer, User, Announcement, GrievanceAppointment, Note, Notification, Member, Officer, FinancialFile
from django.contrib import messages
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.http import JsonResponse
from django.db import IntegrityError, models
from django.utils.timezone import now
from django.utils import timezone
from django.core.paginator import Paginator
from decimal import Decimal
import logging
from cloudinary.api import resource



User = get_user_model()

logger = logging.getLogger(__name__)
# Create your views here.
def is_member(user):
    return user.is_authenticated and user.is_member 

def is_officer(user):
    return user.is_authenticated and user.is_officer

class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and any(getattr(user, role, False) for role in self.allowed_roles):
            return super().dispatch(request, *args, **kwargs)
        return redirect('login')  # Redirect if unauthorized

#views for initial
def home(request):
    return render(request, 'initial/home.html')

def communitymap(request):
    return render(request, 'initial/communitymap.html')

def get_month_calendar(year, month):
    cal_obj = cal.Calendar()
    month_days = cal_obj.monthdayscalendar(year, month)  # List of weeks, each a list of days
    calendar_data = []

    for week in month_days:
        week_data = []
        for day in week:
            if day != 0:  # Avoid 0 days, which are placeholders for empty days in the month
                # Get reservations and announcements for this day
                day_reservations = Reservation.objects.filter(
                    reservation_date=date(year, month, day),
                    status='Confirmed'
                )
                day_appointments = GrievanceAppointment.objects.filter(
                    reservation_date=date(year, month, day),
                    status='Confirmed'
                )
                day_announcements = Announcement.objects.filter(
                    date=date(year, month, day)
                )
                day_data = {
                    'day': day,
                    'reservations': day_reservations,
                    'grievance_appointments': day_appointments,
                    'announcements': day_announcements
                }
            else:
                day_data = {'day': day, 'reservations': [], 'grievance_appointments': [], 'announcements': []}  # No data for placeholder days
            week_data.append(day_data)
        calendar_data.append(week_data)
    
    return calendar_data

def calendar(request, year=None, month=None): 
    today = date.today()

    # Check if a month is selected from the input form
    selected_month_str = request.GET.get('selected_month')
    if selected_month_str:
        # Parse the selected month (format YYYY-MM) to set year and month
        selected_date = datetime.strptime(selected_month_str, "%Y-%m")
        year = selected_date.year
        month = selected_date.month
    elif year is None or month is None:
        year = today.year
        month = today.month
    else:
        year = int(year)
        month = int(month)

    # The rest of the logic remains the same as before.
    month_calendar = get_month_calendar(year, month)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    current_month = date(year, month, 1)
    prev_month_name = (date(year, prev_month, 1)).strftime('%B')
    next_month_name = (date(year, next_month, 1)).strftime('%B')

    context = {
        'calendar': month_calendar,
        'year': year,
        'month': current_month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'prev_month_name': prev_month_name,
        'next_month_name': next_month_name,
    }

    return render(request, 'initial/calendar.html', context)

def news(request):
    latest_news = Newsfeed.objects.filter(created_at__lte=now()).order_by('-created_at').first()
    
    # Fetch all newsfeeds excluding the latest news
    if latest_news:
        newsfeeds = Newsfeed.objects.exclude(pk=latest_news.pk).order_by('-created_at')
    else:
        newsfeeds = Newsfeed.objects.all().order_by('-created_at')
    
    # Fetch the latest announcement with a future or current date
    latest_announcement = Announcement.objects.filter(date__gte=now()).order_by('-date').first()
    
    return render(request, 'initial/news.html', {'newsfeeds': newsfeeds, 'latest_announcement': latest_announcement, 'latest_news': latest_news})
    
def news_article(request, pk):
    newsfeeds = Newsfeed.objects.exclude(id=pk).order_by('-created_at')
    
    # Get the specific newsfeed object
    newsfeed = get_object_or_404(Newsfeed, pk=pk)

    return render(request, 'initial/news-single.html', {
        'newsfeeds': newsfeeds,
        'newsfeed': newsfeed
    })

def about(request):
    officer_hierarchy = {
        'President': 1,
        'Vice President': 2,
        'Secretary': 3,
        'Treasurer': 4,
        'Auditor': 5,
        'P.R.O': 6,
    }
    officers = list(Officer.objects.all())
    officers.sort(key=lambda x: officer_hierarchy.get(x.officer_position, 999))

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")  # Add success message
            return redirect('about')  # Redirect to the same page to clear the form
    else:
        form = ContactForm()

    return render(request, 'initial/about.html', {
        'form': form,
        'officers': officers
    })

def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('subscribe_newsletter')
            except IntegrityError:
                form.add_error('email', 'This email is already subscribed!')
    else:
        form = NewsletterForm()
    return render(request, 'initial/home.html', {'form': form})

class LoginSignupView(View):
    def get(self, request, *args, **kwargs):
        login_form = CustomLoginForm()
        signup_form = UserSignUpForm()
        return render(request, 'initial/login_signup.html', {
            'login_form': login_form,
            'signup_form': signup_form
        })

    def post(self, request, *args, **kwargs):
        if 'login' in request.POST:  # Handle login form submission
            login_form = CustomLoginForm(data=request.POST)
            signup_form = UserSignUpForm()

            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)

                remember = request.POST.get('remember')
                if remember:  # If "Remember Me" is checked
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)  # Default session duration
                else:
                    request.session.set_expiry(0)

                return self.redirect_user(user)

        elif 'signup' in request.POST:  # Handle signup form submission
            signup_form = UserSignUpForm(request.POST)
            login_form = CustomLoginForm()

            if signup_form.is_valid():
                user = signup_form.save(commit=False)  # Save user instance without committing
                user.is_active = False  # Deactivate the account initially
                user.save()  # Save user to the database
                            # Send the email verification link
                send_activation_email(request, user)
                messages.success(request, "Please check your email to verify your account.", extra_tags="sign_up")
                # Create notifications for all officers
                
                self.notify_officers(user)

                return redirect('login')  # Redirect to login page after signup

        # Render the template with errors
        return render(request, 'initial/login_signup.html', {
            'login_form': login_form,
            'signup_form': signup_form
        })

    def redirect_user(self, user):
        """Redirects user to their respective landing page."""
        if user.is_user_officer():
            return redirect(reverse_lazy('officer_landing_page', kwargs={'username': user.username}))
        return redirect(reverse_lazy('member_landing_page', kwargs={'username': user.username}))

    def notify_officers(self, user):
        """Notify all officers about the new user registration."""
        officers = User.objects.filter(is_officer=True).exclude(id=user.id)
        # Create notifications for officers about new member/officer
        if user.is_member:
            notification_message = f"A new member has signed up: {user.username}."
        elif user.is_officer:
            notification_message = f"A new officer has signed up: {user.username}."

        for officer in officers:
            Notification.objects.create(
                recipient=officer,
                content=notification_message,
                created_at=now()
            )

def send_activation_email(request, user):
    try:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = request.build_absolute_uri(reverse('activate', kwargs={'uidb64': uid, 'token': token}))
        
        subject = "Activate Your HOA Account"
        message = render_to_string('initial/activation_email.html', {
            'user': user,
            'activation_link': activation_link,
        })
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email='springvillegardens2hoa@gmail.com',
            to=[user.email],
        )
        email.content_subtype = 'html'
        email.send()
        logger.info(f"Activation email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send activation email to {user.email}: {e}")

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # Send a notification to the user
        Notification.objects.create(
            recipient=user,
            content=f"Welcome, {user.username}! Your account has been successfully activated. Update your profile to access all features!",
            created_at=timezone.now()
        )

        # Notify officers about the user's activation
        officers = User.objects.filter(is_officer=True).exclude(id=user.id)
        for officer in officers:
            Notification.objects.create(
                recipient=officer,
                content=f"The account of {user.username} has been verified and activated.",
                created_at=timezone.now()
            )

        return render(request, 'initial/activation_success.html')  # Create a success template
    else:
        return render(request, 'initial/activation_failed.html')  # Create a failure template
            
def logout_view(request):
    # Log out the user.
    logout(request)
    # Redirect to a success page.
    return redirect('home')

#member_views_dashboard
@login_required
@user_passes_test(is_member, login_url='/login')
def member_landing_page(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')

    user = request.user

    # Initialize all counts to zero
    household_count = 0
    reservation_count = 0
    appointment_count = 0
    request_count = 0
    overdue_count = 0

    try:
        # Fetch the household where the logged-in user is the owner
        household = Household.objects.get(owner_name=user)

        # Count the total number of residents in the household
        household_count = Resident.objects.filter(household=household).count()

        # Count total reservations
        reservation_count = Reservation.objects.filter(household=household, status='Pending').count()

        # Count total appointments
        appointment_count = GrievanceAppointment.objects.filter(household=household, status='Pending').count()

        # Count total requests
        request_count = ServiceRequest.objects.filter(household=household, status='Pending').count()

        # Count total overdues
        overdue_count = Billing.objects.filter(household=household, status='Overdue').count()

    except Household.DoesNotExist:
        # All counts are already initialized to 0

        pass  # You can remove this line, as it's not needed

    # Note functionality
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = user
            note.save()
            return redirect('member_landing_page', username=username)
    else:
        form = NoteForm()

    # Get existing notes
    user_notes = Note.objects.filter(user=user).order_by('-created_at')
    latest_announcement = Announcement.objects.order_by('-date', '-time').first()

    context = {
        'household_count': household_count,
        'reservation_count': reservation_count,
        'appointment_count': appointment_count,
        'request_count': request_count,
        'overdue_count': overdue_count,
        'form': form,
        'user_notes': user_notes,
        'latest_announcement': latest_announcement,
    }

    return render(request, 'member/homeowner_dashboard.html', context)

@login_required
@user_passes_test(is_member, login_url='/login')
def delete_note(request, username, note_id):
    note = get_object_or_404(Note, id=note_id, user__username=username)  # Adjust as necessary based on your Note model structure
    if request.method == 'POST':
        note.delete()
        return redirect('member_landing_page', username=username)  # Redirect back to the landing page after deletion
    return redirect('member_landing_page', username=username)

#member_views_news    
@login_required
@user_passes_test(is_member, login_url='/login')
def newsfeed(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')

    latest_news = Newsfeed.objects.filter(created_at__lte=now()).order_by('-created_at').first()
    # Fetch all newsfeeds excluding the latest news
    if latest_news:
        newsfeeds = Newsfeed.objects.exclude(pk=latest_news.pk).order_by('-created_at')
    else:
        newsfeeds = Newsfeed.objects.all().order_by('-created_at')
    
    # Fetch the latest announcement with a future or current date
    latest_announcement = Announcement.objects.filter(date__gte=now()).order_by('-date').first()
    
    return render(request, 'member/newsfeed/newsfeed.html', {'newsfeeds': newsfeeds, 'latest_announcement': latest_announcement, 'latest_news': latest_news})

@login_required
@user_passes_test(is_member, login_url='/login')
def newsarticle(request, username, pk):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')

    newsfeeds = Newsfeed.objects.exclude(id=pk).order_by('-created_at')
    
    # Get the specific newsfeed object
    newsfeed = get_object_or_404(Newsfeed, pk=pk)

    return render(request, 'member/newsfeed/newsarticle.html', {
        'newsfeeds': newsfeeds,
        'newsfeed': newsfeed
    })
    
#member_views_household
class HouseholdDetailsView(RoleRequiredMixin, TemplateView):
    allowed_roles = ['is_member']
    template_name = 'member/household/household_detail.html'

    def get(self, request, username):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')

        user = request.user
        try:
            household = Household.objects.get(owner_name=user)
        except Household.DoesNotExist:
            return redirect('add_household', username=request.user.get_username())  # Redirect if no household exists

        # Fetch residents and billings related to the household
        residents = Resident.objects.filter(household=household)
        billings = Billing.objects.filter(household=household)

        context = {
            'household': household,
            'residents': residents,
            'billings': billings
        }
        return render(request, self.template_name, context)

@login_required
@user_passes_test(is_member, login_url='/login')
def add_household(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')

    user = request.user
    
    # Check if the user's profile is updated
    if not user.fname or not user.lname:
        messages.warning(request, "Please update your profile with your first and last name before adding a household.", extra_tags="update_prof")
        return redirect('member_update_profile', username=request.user.username)  # Redirect to profile update page

    if request.method == 'POST':
        form = HouseholdForm(request.POST)
        if form.is_valid():
            household = form.save(commit=False)
            household.owner_name = request.user
            household.save()
            
            # Fetch existing billing months
            existing_billing_months = Billing.objects.values_list('billing_month', flat=True).distinct()

            # Create billing entries for the new household
            for billing_month in existing_billing_months:
                Billing.objects.create(
                    household=household,
                    billing_month=billing_month,
                    amount=300.00,  # Default amount; you can customize this
                    status='Unpaid'  # Default status; you can customize this
                )

            messages.success(request, "Household added successfully!", extra_tags="household_update")
            
            # Create a notification for all officers
            from django.contrib.auth import get_user_model
            User = get_user_model()  # Ensure you are using the correct User model
            officers = User.objects.filter(is_officer=True)  # Assuming the User model has the 'is_officer' flag
            
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,  # Link to the officer directly
                    content=f"A new household has been added by {user.fname} {user.lname}.",
                    created_at=timezone.now()
                )

            return redirect('household_detail', username=request.user.get_username())
    else:
        form = HouseholdForm()

    # Pass the choices to the template context
    block_choices = Household.BLOCK_CHOICES
    street_choices = Household.STREET_CHOICES
    home_tenure_choices = Household.HOME_TENURE_CHOICES
    land_tenure_choices = Household.LAND_TENURE_CHOICES
    construction_choices = Household.CONSTRUCTION_CHOICES
    kitchen_choices = Household.KITCHEN_CHOICES
    water_facility_choices = Household.WATER_FACILITY_CHOICES
    toilet_facility_choices = Household.TOILET_FACILITY_CHOICES

    return render(request, 'member/household/add_household.html', {
        'form': form,
        'block_choices': block_choices,
        'street_choices': street_choices,
        'home_tenure_choices': home_tenure_choices,
        'land_tenure_choices': land_tenure_choices,
        'construction_choices': construction_choices,
        'kitchen_choices': kitchen_choices,
        'water_facility_choices': water_facility_choices,
        'toilet_facility_choices': toilet_facility_choices,
    })

class edit_household(RoleRequiredMixin, View):
    allowed_roles = ['is_member']
    def get(self, request, username):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')

        household = get_object_or_404(Household, owner_name=request.user)
        form = HouseholdForm(instance=household)
        return render(request, 'member/household/edit_household.html', {'form': form, 'household': household})

    def post(self, request, username):
        household = get_object_or_404(Household, owner_name=request.user)
        form = HouseholdForm(request.POST, instance=household)
        
        if form.is_valid():
            form.save()

            messages.success(request, "Household updated successfully!", extra_tags="household_update")
            # Create a notification for all officers after successfully editing the household
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                # Create the notification content (you can customize this message)
                content = f"The household of {household.owner_name} has been updated."

                # Create and save the notification
                Notification.objects.create(
                    recipient=officer,
                    content=content,
                    created_at=timezone.now()
                )

            return redirect('household_detail', username=username)
        
        return render(request, 'member/household/edit_household.html', {'form': form, 'household': household})

#member_views_resident
@login_required
@user_passes_test(is_member, login_url='/login')
def resident_detail(request, username, pk):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    resident = get_object_or_404(Resident, pk=pk)
    return render(request, 'member/household/resident_detail.html', {'resident': resident})

@login_required
@user_passes_test(is_member, login_url='/login')
def add_resident(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    household = get_object_or_404(Household, owner_name=request.user)
    
    if request.method == "POST":
        form = ResidentForm(request.POST)
        if form.is_valid():
            resident = form.save(commit=False)
            resident.household = household  # Assign the household
            resident.save()

            messages.success(request, "Resident added successfully!", extra_tags="household_update")
            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                content = f"A new resident has been added to the household of {household.owner_name}: {resident.first_name} {resident.last_name}."

                # Create and save the notification
                Notification.objects.create(
                    recipient=officer,
                    content=content,
                    created_at=timezone.now()  # Current time using timezone-aware datetime
                )

            return redirect('household_detail', username=username)
    else:
        form = ResidentForm()

    gender_choices = Resident.GENDER_CHOICES
    civil_status_choices = Resident.CIVIL_STATUS_CHOICES
    religion_choices = Resident.RELIGION_CHOICES
    educational_attainment_choices = Resident.EDUCATIONAL_ATTAINMENT_CHOICES

    return render(request, 'member/household/add_edit_resident.html', {
        'form': form, 
        'household': household,
        'gender_choices': gender_choices,
        'civil_status_choices': civil_status_choices,
        'religion_choices': religion_choices,
        'educational_attainment_choices': educational_attainment_choices
    })

@login_required
@user_passes_test(is_member, login_url='/login')
def edit_resident(request, username, pk):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    resident = get_object_or_404(Resident, pk=pk)
    
    if request.method == "POST":
        form = ResidentForm(request.POST, instance=resident)
        if form.is_valid():
            # Save the updated resident
            resident = form.save()

            messages.success(request, "Resident updated successfully!", extra_tags="resident_update")
            # Create a notification for all officers about the update
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                content = f"The details of the resident {resident.first_name} {resident.last_name} have been updated in the household of {resident.household.owner_name}."

                # Create and save the notification
                Notification.objects.create(
                    recipient=officer,
                    content=content,
                    created_at=timezone.now()  # Current time using timezone-aware datetime
                )

            return redirect('resident_detail', username=username, pk=resident.pk)
    else:
        form = ResidentForm(instance=resident)

    gender_choices = Resident.GENDER_CHOICES
    civil_status_choices = Resident.CIVIL_STATUS_CHOICES
    religion_choices = Resident.RELIGION_CHOICES
    educational_attainment_choices = Resident.EDUCATIONAL_ATTAINMENT_CHOICES

    return render(request, 'member/household/add_edit_resident.html', {
        'form': form, 
        'resident': resident,
        'gender_choices': gender_choices,
        'civil_status_choices': civil_status_choices,
        'religion_choices': religion_choices,
        'educational_attainment_choices': educational_attainment_choices
    })

@login_required
@user_passes_test(is_member, login_url='/login')
def delete_resident(request, username, pk):
    resident = get_object_or_404(Resident, pk=pk)
    
    if request.method == 'POST':
        # Store the name of the resident to be deleted for notification content
        deleted_resident_name = f"{resident.first_name} {resident.last_name}"

        # Delete the resident
        resident.delete()
        
        messages.success(request, "Resident has been deleted!", extra_tags="household_update")
        # Create a notification for all officers about the resident's deletion
        officers = User.objects.filter(is_officer=True)
        for officer in officers:
            content = f"The resident {deleted_resident_name} has been deleted from the household of {resident.household.owner_name}."
            
            # Create and save the notification
            Notification.objects.create(
                recipient=officer,
                content=content,
                created_at=timezone.now()  # Current time using timezone-aware datetime
            )

        messages.success(request, "Resident deleted successfully.")
        return redirect('household_detail', username=username)
    
    else:
        messages.error(request, "Invalid request method.")
        return redirect('household_detail', username=username)

#member_views_billing
@login_required
@user_passes_test(is_member, login_url='/login')
def create_payment_link(request, username, billing_id):
    # Fetch the billing object using the billing_id
    billing = get_object_or_404(Billing, id=billing_id)

    # Use PayMongo test endpoint (as per your provided URL for testing)
    url = "https://api.paymongo.com/v1/links"

    # Prepare the payload
    payload = {
        "data": {
            "attributes": {
                "amount": int(billing.amount * 100),  # Convert to centavos
                "description": f"Payment for {billing.billing_month.strftime('%B %Y')} dues",
                "remarks": "GCASH Payment",
            }
        }
    }

    # Use the test secret key
    secret_key = settings.PAYMONGO_SECRET_KEY  # Ensure this is set in settings
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {base64.b64encode(secret_key.encode()).decode()}",
    }

    try:
        # Make the API request
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses

        # Parse the API response
        response_data = response.json()
        if response.status_code == 200 and "data" in response_data:
                link_status = response_data["data"]["attributes"]["status"]
                if link_status == "unpaid":
                    # Update billing status
                    billing.status = "Paid"
                    billing.save()

                    messages.success(request, "Billing month paid successfully!", extra_tags="household_update")
                    # Send notification to all officers except the one who triggered the action
                    officers = User.objects.filter(is_officer=True).exclude(id=request.user.id)
                    for officer in officers:
                        Notification.objects.create(
                            recipient=officer,
                            content=f"A payment link for {billing.billing_month.strftime('%B %Y')} has been created and marked as 'Paid'.",
                            created_at=timezone.now()
                        )
                    # Extract the checkout URL
        checkout_url = response_data["data"]["attributes"].get("checkout_url")

        if not checkout_url:
            return JsonResponse({"error": "Failed to generate a valid checkout URL."}, status=500)

        # Redirect the user to the PayMongo checkout page
        return redirect(checkout_url)  # This will take the user to the checkout interface

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Request failed: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

#member_views_reservation
class MyReservation(RoleRequiredMixin, ListView):
    allowed_roles = ['is_member']
    model = Reservation
    template_name = 'member/reservation/my_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        # Ensure the logged-in user matches the username in the URL
        if self.request.user.username != self.kwargs.get('username'):
            messages.error(self.request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')

        # Attempt to get the household of the currently logged-in user
        try:
            self.household = Household.objects.get(owner_name=self.request.user)
        except Household.DoesNotExist:
            # If no household exists, return an empty queryset
            self.household = None
            return Reservation.objects.none()

        # If a household exists, filter the reservations by this household
        queryset = super().get_queryset().filter(household=self.household)

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(amenities__icontains=search_query) |
                Q(reservation_date__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

        # Check if the user has a household
        context['no_household'] = self.household is None

        # Add pagination
        reservations = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(reservations, 6)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['reservations'] = page_obj

        return context

@login_required
@user_passes_test(is_member, login_url='/login')
def make_reservation(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = request.user
    try:
        # Ensure we're getting the correct Household instance
        household = Household.objects.get(owner_name=user)
    except Household.DoesNotExist:
        # Handle the case where the user has no associated household
        messages.error(request, "You do not have an associated household.")
        return redirect('add_household', username=username)  # Redirect to a page to create a household

    is_owner = household.owner_name == user
    reservations = household.reservations.all()

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation_date = form.cleaned_data.get('reservation_date')
            reservation_start = form.cleaned_data.get('reservation_time_start')
            reservation_end = form.cleaned_data.get('reservation_time_end')

            # Check if the reservation date is in the past
            if reservation_date and reservation_date < date.today():
                messages.error(request, "Reservation date cannot be in the past.")
                return redirect('make_reservation', username=username)

            # Check if the start time is before the end time
            if reservation_start and reservation_end and reservation_start >= reservation_end:
                messages.error(request, "Start time must be before end time.")
                return redirect('make_reservation', username=username)

            # Check for existing reservations with the same date and time
            existing_reservation = Reservation.objects.filter(
                household=household,
                reservation_date=reservation_date,
                reservation_time_start__lt=reservation_end,
                reservation_time_end__gt=reservation_start
            ).exists()

            if existing_reservation:
                messages.error(request, "A reservation already exists for this time slot.")
                return redirect('make_reservation', username=username)

            # Save the reservation
            reservation = form.save(commit=False)
            reservation.household = household
            reservation.save()

            # Success message for creating reservation
            messages.success(request, "Reservation created successfully!", extra_tags="reservation_created")

            # Create a notification for all officers, except the user who made the reservation
            officers = User.objects.filter(is_officer=True).exclude(id=user.id)
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,  # Link to officer directly
                    content=f"A new reservation has been made by {user.fname} {user.lname} for the household {household.owner_name}.",
                    created_at=timezone.now()  # Use current time for the notification
                )

            # Redirect to the same page or another page with the success message
            return redirect('make_reservation', username=username)

    else:
        form = ReservationForm()

    return render(request, 'member/reservation/reservation_form.html', {
        'form': form,
        'user': user,
        'household': household,
        'reservations': reservations,
        'is_owner': is_owner,
    })

@login_required
@user_passes_test(is_member, login_url='/login')
def update_reservation(request, username, request_id):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    reservation = get_object_or_404(Reservation, id=request_id)
    user = request.user
    household = reservation.household  # Get the household associated with the reservation

    if request.method == 'POST':
        form = ReservationForm(request.POST, request.FILES, instance=reservation)
        if form.is_valid():
            # Get cleaned data
            reservation_date = form.cleaned_data.get('reservation_date')
            reservation_start = form.cleaned_data.get('reservation_time_start')
            reservation_end = form.cleaned_data.get('reservation_time_end')

            # Check if the reservation date is in the past
            if reservation_date and reservation_date < date.today():
                messages.error(request, "Reservation date cannot be in the past.")
                return redirect('update_reservation', username=username, request_id=request_id)

            # Check if the start time is before the end time
            if reservation_start and reservation_end and reservation_start >= reservation_end:
                messages.error(request, "Start time must be before end time.")
                return redirect('update_reservation', username=username, request_id=request_id)

            # Check for overlapping reservations with the same details
            existing_reservation = Reservation.objects.filter(
                household=household,
                reservation_date=reservation_date,
                reservation_time_start__lt=reservation_end,
                reservation_time_end__gt=reservation_start
            ).exclude(id=reservation.id).exists()  # Exclude the current reservation

            if existing_reservation:
                messages.error(request, "A reservation already exists for this time slot.")
                return redirect('update_reservation', username=username, request_id=request_id)

            # Save the form if no conflict is found
            form.save()

            # Success message for updating reservation
            messages.success(request, "Reservation updated successfully!", extra_tags="reservation_updated")

            # Create a notification for all officers, except the user who updated the reservation
            officers = User.objects.filter(is_officer=True).exclude(id=user.id)
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,
                    content=f"The reservation for household {reservation.household.owner_name} has been updated by {user.fname} {user.lname}.",
                    created_at=timezone.now()  # Use current time for the notification
                )

            # Redirect to the same page with a success message or another page
            return redirect('update_reservation', username=username, request_id=request_id)

    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'member/reservation/update_reservation.html', {
        'form': form,
        'reservation': reservation,
    })

@login_required
@user_passes_test(is_member, login_url='/login')
def cancel_reservation(request, username, request_id):
    reservation = get_object_or_404(Reservation, id=request_id)
    user = request.user
    
    if request.method == 'POST':
        reservation.status = 'Canceled'  # Update the status to 'Canceled' or your equivalent status
        reservation.save()

        
        messages.success(request, "Reservation has been canceled!", extra_tags="reservation_canceled")
        # Create a notification for all officers
        officers = User.objects.filter(is_officer=True)
        for officer in officers:
            notification = Notification.objects.create(
                recipient=officer,  # Send notification to officer
                content=f"The reservation for household {reservation.household.owner_name} has been canceled by {user.fname} {user.lname}.",
                created_at=timezone.now()  # Use the current time for the notification
            )
            notification.save()

        messages.success(request, 'Reservation has been canceled successfully!')
        return redirect('my_reservation', username=request.user.username)
    else:
        # If it's a GET request, show the confirmation page
        return render(request, 'member/reservation/cancel_confirmation.html', {'reservation': reservation})

#member_views_request
class MyRequest(RoleRequiredMixin, ListView):
    allowed_roles = ['is_member']
    model = ServiceRequest
    template_name = 'member/services/my_requests.html'
    context_object_name = 'service_requests'

    def get_queryset(self):
        # Ensure the logged-in user matches the username in the URL
        if self.request.user.username != self.kwargs.get('username'):
            messages.error(self.request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')

        # Attempt to get the household of the currently logged-in user
        try:
            self.household = Household.objects.get(owner_name=self.request.user)
        except Household.DoesNotExist:
            # If no household exists, return an empty queryset
            self.household = None
            return ServiceRequest.objects.none()

        queryset = super().get_queryset().filter(household=self.household)

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(service_type__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

        context['no_household'] = self.household is None

        # Add pagination
        service_requests = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(service_requests, 6)  # Show 6 service requests per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['service_requests'] = page_obj

        return context

@login_required
@user_passes_test(is_member, login_url='/login')
def submit_request(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = request.user
    try:
        # Ensure we're getting the correct Household instance
        household = Household.objects.get(owner_name=user)
    except Household.DoesNotExist:
        # Handle the case where the user has no associated household
        messages.error(request, "You do not have an associated household.")
        return redirect('add_household', username=username)  # Redirect to a page to create a household
    
    is_owner = household.owner_name == user
    servicerequests = household.service_requests.all()

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            servicetype = form.cleaned_data.get('service_type')
            
            existing_request = ServiceRequest.objects.filter(
                household=household,
                service_type=servicetype,  # Ensure the variable matches
                title=title,
            ).exists()

            if existing_request:
                messages.error(request, "A similar service request already exists.")
                return redirect('submit_request', username=username)

            # Assign the household instance, not the user
            service_request = form.save(commit=False)
            service_request.household = household
            service_request.save()

            messages.success(request, "Request created successfully!", extra_tags="request_created")
            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"A new request has been submitted by {user.fname} {user.lname} for household {household.owner_name}.",
                    created_at=timezone.now()  # Use the current time for the notification
                )
                notification.save()

            return redirect('submit_request', username=username)
        else:
            messages.error(request, f"Form submission failed: {form.errors}")
            return redirect('submit_request', username=username)
    else:
        form = ServiceRequestForm()

    return render(request, 'member/services/submit_request.html', {
        'form': form,
        'user': user,
        'household': household,
        'servicerequests': servicerequests,
        'is_owner': is_owner,
    })

@login_required
@user_passes_test(is_member, login_url='/login')
def update_request(request, username, request_id):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    household = service_request.household  # Get the household instance
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, request.FILES, instance=service_request)
        if form.is_valid():
            # Get cleaned data
            service_type = form.cleaned_data.get('service_type')
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')

            # Check for duplicate service requests (same service type, title, and description)
            existing_request = ServiceRequest.objects.filter(
                household=household,
                service_type=service_type,
                title=title,
                description=description
            ).exclude(id=service_request.id).exists()  # Exclude the current request

            if existing_request:
                messages.error(request, "A similar service request already exists.")
                return redirect('update_request', username=username, request_id=request_id)

            form.save()

            messages.success(request, "Request updated successfully!", extra_tags="request_updated")
            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"The request #{service_request.id} has been updated by {request.user.fname} {request.user.lname}.",
                    created_at=timezone.now()  # Use the current time for the notification
                )
                notification.save()

            return redirect('update_request', username=username, request_id=request_id)
    else:
        form = ServiceRequestForm(instance=service_request)

    return render(request, 'member/services/update_request.html', {'form': form, 'service_request': service_request})

@login_required
@user_passes_test(is_member, login_url='/login')
def cancel_request(request, username, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    if request.method == 'POST':
        service_request.status = 'Canceled'  # Or your equivalent status
        service_request.save()

        messages.success(request, "Request has been canceled!", extra_tags="request_canceled")
        # Create a notification for all officers
        officers = User.objects.filter(is_officer=True)
        for officer in officers:
            notification = Notification.objects.create(
                recipient=officer,  # Send notification to officer
                content=f"The request #{service_request.id} has been canceled by {request.user.fname} {request.user.lname}.",
                created_at=timezone.now()  # Use the current time for the notification
            )
            notification.save()

        return redirect('my_request', username=username)
    else:
        # If it's a GET request, show the confirmation page
        return render(request, 'member/services/cancel_confirmation.html', {'service_request': service_request})

#member_views_appointment
class MyAppointment(RoleRequiredMixin, ListView):
    allowed_roles = ['is_member']
    model = GrievanceAppointment
    template_name = 'member/grievance/my_appointments.html'
    context_object_name = 'grievance_appointments'
    
    def get_queryset(self):
        if self.request.user.username != self.kwargs.get('username'):
            messages.error(self.request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        # Attempt to get the household of the currently logged-in user
        try:
            self.household = Household.objects.get(owner_name=self.request.user)
        except Household.DoesNotExist:
            # If no household exists, return an empty queryset
            self.household = None
            return GrievanceAppointment.objects.none()

        queryset = super().get_queryset().filter(household=self.household)

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(appointment_type__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(reservation_date__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

        context['no_household'] = self.household is None
        
         # Add pagination
        grievance_appointments = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(grievance_appointments, 5)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['grievance_appointments'] = page_obj

        return context

@login_required
@user_passes_test(is_member, login_url='/login')
def make_appointment(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = request.user
    try:
        household = Household.objects.get(owner_name=user)
    except Household.DoesNotExist:
        # Handle the case where the user has no associated household
        messages.error(request, "You do not have an associated household.")
        return redirect('add_household', username=username)  # Redirect to a page to create a household

    is_owner = household.owner_name == user if household else False
    grievanceappointments = household.grievance_appointments.all() if household else []

    if request.method == 'POST':
        form = GrievanceForm(request.POST, request.FILES)
        if form.is_valid():
            reservation_date = form.cleaned_data.get('reservation_date')

            # Check for existing appointment for the same household on the same date
            existing_appointment = GrievanceAppointment.objects.filter(
                household=household,
                reservation_date=reservation_date
            ).exists()

            if existing_appointment:
                messages.error(request, "An appointment already exists for this date.")
                return redirect('make_appointment', username=username)

            grievance_appointment = form.save(commit=False)
            grievance_appointment.household = household
            grievance_appointment.save()

            messages.success(request, "Appointment created successfully!", extra_tags="appointment_created")
            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"A new appointment has been created by {request.user.fname} {request.user.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            messages.success(request, 'Appointment created successfully!')
            return redirect('make_appointment', username=username)
    else:
        form = GrievanceForm()

    return render(request, 'member/grievance/make_appointment.html', {
        'form': form,
        'user': user,
        'household': household,
        'grievanceappointments': grievanceappointments,
        'is_owner': is_owner,
    })

@login_required
@user_passes_test(is_member, login_url='/login')
def update_appointment(request, username, request_id):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    grievance_appointment = get_object_or_404(GrievanceAppointment, id=request_id)
    user = request.user
    household = grievance_appointment.household  # Get the household associated with the appointment

    if request.method == 'POST':
        form = GrievanceForm(request.POST, request.FILES, instance=grievance_appointment)
        if form.is_valid():
            reservation_date = form.cleaned_data.get('reservation_date')

            # Check for existing appointment for the same household on the same date (excluding current appointment)
            existing_appointment = GrievanceAppointment.objects.filter(
                household=household,
                reservation_date=reservation_date
            ).exclude(id=grievance_appointment.id).exists()

            if existing_appointment:
                messages.error(request, "An appointment already exists for this date.")
                return redirect('update_appointment', username=username, request_id=request_id)

            form.save()

            messages.success(request, "Appointment updated successfully!", extra_tags="appointment_updated")
            # Create a notification for all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,
                    content=f"The appointment #{grievance_appointment.id} has been updated by {request.user.fname} {request.user.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            messages.success(request, 'Appointment updated successfully!')
            return redirect('update_appointment', username=username, request_id=request_id)
    else:
        form = GrievanceForm(instance=grievance_appointment)

    return render(request, 'member/grievance/update_appointment.html', {
        'form': form,
        'grievance_appointment': grievance_appointment,
    })
    
@login_required
@user_passes_test(is_member, login_url='/login')
def cancel_appointment(request, username, request_id):
    grievance_appointment = get_object_or_404(GrievanceAppointment, id=request_id)
    if request.method == 'POST':
        grievance_appointment.status = 'Canceled'  # Or your equivalent status
        grievance_appointment.save()

        
        messages.success(request, "Appointment has been canceled!", extra_tags="appointment_canceled")
        # Create a notification for all officers
        officers = User.objects.filter(is_officer=True)
        for officer in officers:
            notification = Notification.objects.create(
                recipient=officer,  # Send notification to officer
                content=f"The appointment #{grievance_appointment.id} has been canceled by {request.user.fname} {request.user.lname}.",
                created_at=timezone.now()
            )
            notification.save()

        return redirect('my_appointment', username=username)
    else:
        # If it's a GET request, show the confirmation page
        return render(request, 'member/grievance/cancel_confirmation.html', {'grievance_appointment': grievance_appointment})

#member_views_profile
@login_required
@user_passes_test(is_member, login_url='/login')
def member_profile_info(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = request.user
    return render(request, 'member/profile/profile_info.html', {
        'user': user
    })

@login_required
@user_passes_test(is_member, login_url='/login')
def member_update_profile(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = User.objects.get(username=username)

    if request.method == 'POST':
        form = MemberChangeForm(request.POST, request.FILES, instance=user)

        if form.is_valid():

            user = form.save(commit=False)

            user.save()

            messages.success(request, "Profile updated successfully!", extra_tags="profile_updated")
            
            # Send notifications to all officers
            officers = User.objects.filter(is_officer=True)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"The profile of member {user.fname} {user.lname} has been updated.",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('member_profile_info', username=user.username)
    else:
        form = MemberChangeForm(instance=user)

    return render(request, 'member/profile/profile_update.html', {'form': form})

@login_required
@user_passes_test(is_member, login_url='/login')
def member_delete_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()

        # Send notifications to all officers
        officers = User.objects.filter(is_officer=True)
        for officer in officers:
            notification = Notification.objects.create(
                recipient=officer,  # Send notification to officer
                content=f"The profile of member {user.fname} {user.lname} has been deleted.",
                created_at=timezone.now()
            )
            notification.save()

        messages.success(request, "Your account has been deleted.")
        return redirect('home')
    else:
        messages.error(request, "Invalid request.")
        return redirect('member_profile_info', username=request.user.username)

#member_views_notifications
class MemberNotificationsView(RoleRequiredMixin, View):
    allowed_roles = ['is_member']
    def get(self, request, *args, **kwargs):
        filter_type = request.GET.get('filter', 'all')  # Default to 'all'
        notifications = Notification.objects.filter(recipient=request.user)

        if filter_type == 'unread':
            notifications = notifications.filter(read=False)
        elif filter_type == 'read':
            notifications = notifications.filter(read=True)

        return render(request, 'member/sidebar.html', {
            'notifications': notifications
        })

#member_views_calendar
@login_required
@user_passes_test(is_member, login_url='/login')
def eventscalendar(request, username, year=None, month=None): 
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    today = date.today()

    # Check if a month is selected from the input form
    selected_month_str = request.GET.get('selected_month')
    if selected_month_str:
        # Parse the selected month (format YYYY-MM) to set year and month
        selected_date = datetime.strptime(selected_month_str, "%Y-%m")
        year = selected_date.year
        month = selected_date.month
    elif year is None or month is None:
        year = today.year
        month = today.month
    else:
        year = int(year)
        month = int(month)

    # The rest of the logic remains the same as before.
    month_calendar = get_month_calendar(year, month)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    current_month = date(year, month, 1)
    prev_month_name = (date(year, prev_month, 1)).strftime('%B')
    next_month_name = (date(year, next_month, 1)).strftime('%B')

    context = {
        'calendar': month_calendar,
        'year': year,
        'month': current_month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'prev_month_name': prev_month_name,
        'next_month_name': next_month_name,
    }

    return render(request, 'member/events/calendar.html', context)

#member_views_reports
@login_required
@user_passes_test(is_member, login_url='/login')
def financial_status(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = request.user
    files = FinancialFile.objects.all()

     # Get search query from request
    search_query = request.GET.get('search', '')
    if search_query:
        files = files.filter(
            Q(title__icontains=search_query) |
            Q(uploaded_at__icontains=search_query)
        )

    # Get sorting criteria from query parameters
    sort_by = request.GET.get('sort', 'uploaded_at')  # Default sort by `uploaded_at`
    direction = request.GET.get('direction', 'desc')  # Default direction is descending

    # Sort files based on the selected column and direction
    if sort_by in ['title', 'uploaded_at']:
        files = files.order_by(f"{'' if direction == 'asc' else '-'}{sort_by}")
    else:
        files = files.order_by('-uploaded_at')  # Default fallback sorting

    # Paginate the results
    paginator = Paginator(files, 6)  # Show 6 files per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prepare context for the template
    context = {
        'files': page_obj,
        'sort_by': sort_by,
        'direction': direction,
        'search_query': search_query,
    }

    return render(request, 'member/financial_status.html', context)

@login_required
@user_passes_test(is_member, login_url='/login')
def download_file(request, username, file_id):
    financial_file = get_object_or_404(FinancialFile, id=file_id)
    response = HttpResponse(financial_file.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{financial_file.file.name.split("/")[-1]}"'
    return response

#officer_views_dashboard
@login_required
@user_passes_test(is_officer, login_url='/login')
def officer_landing_page(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = request.user
    
    # Check if the user's profile is updated
    if not user.fname or not user.lname:
        messages.warning(request, "Update your profile first!", extra_tags="officer_update_prof")
        return redirect('officer_update_profile', username=request.user.username)  # Redirect to profile update page

    total_households = Household.objects.count()
    total_residents = Resident.objects.count()
    pending_reservations = Reservation.objects.filter(status='Pending').count()
    pending_requests = ServiceRequest.objects.filter(status='Submitted').count()
    pending_appointments = GrievanceAppointment.objects.filter(status='Pending').count()
    overdue_count = Billing.objects.filter(status='Overdue').count()
    total_users = User.objects.filter(is_superuser=False).count()

    # For graphs:
    # Fetch confirmed reservations grouped by amenity
    amenity_usage = Reservation.objects.filter(status='Confirmed').values('amenities').annotate(count=models.Count('amenities'))

    # Demographics
    sex_demographics = Resident.objects.values('gender').annotate(total=Count('gender'))
    
    # Calculate age demographics (for example, you can create ranges)
    today = date.today()
    age_ranges = [
        ('0-17', 0, 17),
        ('18-24', 18, 24),
        ('25-34', 25, 34),
        ('35-44', 35, 44),
        ('45-54', 45, 54),
        ('55-64', 55, 64),
        ('65+', 65, 100)
    ]
    age_demographics = []
    for label, min_age, max_age in age_ranges:
        count = Resident.objects.filter(birthdate__year__gte=today.year - max_age).filter(birthdate__year__lt=today.year - min_age).count()
        age_demographics.append({'age_range': label, 'total': count})

    home_tenure_demographics = Household.objects.values('home_tenure').annotate(total=Count('home_tenure'))
    land_tenure_demographics = Household.objects.values('land_tenure').annotate(total=Count('land_tenure'))

    # Initialize a counter for vehicle types
    vehicle_count = Counter()

    # Iterate over all households and count each vehicle type
    households = Household.objects.all()
    for household in households:
        if household.vehicles_owned:
            # Split the vehicles owned and count them
            vehicles = household.vehicles_owned.split(', ')
            vehicle_count.update(vehicles)

    # Prepare the vehicle demographics as a list of dictionaries
    vehicle_demographics = [{'vehicles_owned': vehicle, 'total': count} for vehicle, count in vehicle_count.items()]
    # Count entries for the chart
    reservation_count = Reservation.objects.count()
    appointment_count = GrievanceAppointment.objects.count()
    request_count = ServiceRequest.objects.count()
    
    context = {
        'total_households': total_households,
        'total_residents': total_residents,
        'pending_reservations': pending_reservations,
        'pending_requests': pending_requests,
        'pending_appointments': pending_appointments,
        'overdue_count': overdue_count,
        'total_users': total_users,
        'amenity_usage': list(amenity_usage),
        'sex_demographics': list(sex_demographics),
        'age_demographics': age_demographics,
        'home_tenure_demographics': list(home_tenure_demographics),
        'land_tenure_demographics': list(land_tenure_demographics),
        'vehicle_demographics': vehicle_demographics,
        'reservation_count': reservation_count,
        'appointment_count': appointment_count,
        'request_count': request_count
    }

    return render(request, 'officer/officer_dashboard.html', context)

@login_required
@user_passes_test(is_officer, login_url='/login')
def news_feed(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = request.user
    
    # Check if the user's profile is updated
    if not user.fname or not user.lname:
        messages.warning(request, "Update your profile first!", extra_tags="officer_update_prof")
        return redirect('officer_update_profile', username=request.user.username)  # Redirect to profile update page
    # Retrieve newsfeeds and announcements
    newsfeeds = Newsfeed.objects.all().order_by('-created_at')
    announcements = Announcement.objects.all().order_by('-date', '-time')
    
    # Paginate newsfeeds (example: 5 per page)
    paginator_newsfeeds = Paginator(newsfeeds, 3)  # Show 5 newsfeeds per page
    page_number_newsfeeds = request.GET.get('page_newsfeeds')  # Get the current page number for newsfeeds
    page_obj_newsfeeds = paginator_newsfeeds.get_page(page_number_newsfeeds)  # Retrieve the page object for newsfeeds

    # Paginate announcements (example: 3 per page)
    paginator_announcements = Paginator(announcements, 3)  # Show 3 announcements per page
    page_number_announcements = request.GET.get('page_announcements')  # Get the current page number for announcements
    page_obj_announcements = paginator_announcements.get_page(page_number_announcements)  # Retrieve the page object for announcements

    # Context for the template
    context = {
        'newsfeeds': page_obj_newsfeeds,  # Use the paginated page object for newsfeeds
        'announcements': page_obj_announcements,  # Use the paginated page object for announcements
        'page_obj_newsfeeds': page_obj_newsfeeds,  # Optional: explicitly pass page_obj_newsfeeds for pagination controls
        'page_obj_announcements': page_obj_announcements,  # Optional: explicitly pass page_obj_announcements for pagination controls
    }

    # Render the template with the context
    return render(request, 'officer/newsfeed/news_list.html', context)
    
@login_required
@user_passes_test(is_officer, login_url='/login')
def news_single(request, username, pk):
    # Check if the username in the URL matches the logged-in user
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    
    # Get all newsfeeds except the one with the specified pk
    newsfeeds = Newsfeed.objects.exclude(id=pk).order_by('-created_at')
    
    # Get the specific newsfeed object
    newsfeed = get_object_or_404(Newsfeed, pk=pk)
    
    # Render the template with both the specific newsfeed and the filtered list of newsfeeds
    return render(request, 'officer/newsfeed/news_article.html', {
        'newsfeeds': newsfeeds,
        'newsfeed': newsfeed
    })

@login_required
@user_passes_test(is_officer, login_url='/login')
def add_news(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    if request.method == "POST":
        form = NewsfeedForm(request.POST, request.FILES)  # Add request.FILES to handle image files
        if form.is_valid():
            newsfeed = form.save(commit=False)
            newsfeed.written_by = request.user  # Correctly assign the current user
            newsfeed.save()

            
            messages.success(request, "New article created succesfully!", extra_tags="add_news")
            # Send notifications to all officers except the one who wrote the news article
            officers = User.objects.filter(is_officer=True).exclude(id=request.user.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"A new news article has been posted by {request.user.fname} {request.user.lname}: {newsfeed.title}",
                    created_at=timezone.now()
                )
                notification.save()

            # Send notifications to all members
            members = User.objects.filter(is_member=True)
            for member in members:
                notification = Notification.objects.create(
                    recipient=member,  # Send notification to member
                    content=f"A new news article has been posted: {newsfeed.title}",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('add_news', username=username)
    else:
        form = NewsfeedForm()

    return render(request, 'officer/newsfeed/add_edit_news.html', {'form': form})

@login_required
@user_passes_test(is_officer, login_url='/login')
def delete_news(request, username, pk):
    newsfeed = get_object_or_404(Newsfeed, pk=pk)
    if request.method == 'POST':
        newsfeed.delete()
        
        messages.success(request, "Article deleted successfully!", extra_tags="update_news")

        return redirect('news_feed', username=username)
    return redirect('news_feed', username=username)

@login_required
@user_passes_test(is_officer, login_url='/login')
def edit_news(request, username, pk):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    newsfeed = get_object_or_404(Newsfeed, pk=pk)
    if request.method == "POST":
        form = NewsfeedForm(request.POST, request.FILES, instance=newsfeed)  # Ensure to include request.FILES for image handling
        if form.is_valid():
            # Store the officer who is editing the news article
            editing_officer = request.user
            
            # Save the updated newsfeed
            form.save()
            
            messages.success(request, "Article updated successfully!", extra_tags="update_news")
            # Send notifications to all officers except the one who edited the news article
            officers = User.objects.filter(is_officer=True).exclude(id=editing_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"A news article titled '{newsfeed.title}' has been updated by {editing_officer.fname} {editing_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            # Send notifications to all members
            members = User.objects.filter(is_member=True)
            for member in members:
                notification = Notification.objects.create(
                    recipient=member,  # Send notification to member
                    content=f"A news article titled '{newsfeed.title}' has been updated.",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('news_feed', username=username)
    else:
        form = NewsfeedForm(instance=newsfeed)  # Correctly use NewsForm with the news instance

    return render(request, 'officer/newsfeed/add_edit_news.html', {'form': form, 'newsfeed': newsfeed})

#officer_views_announcement
@login_required
@user_passes_test(is_officer, login_url='/login')
def create_announcement(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            # Store the officer who is creating the announcement
            creating_officer = request.user
            
            # Save the new announcement
            announcement = form.save()
            
            messages.success(request, "New announcement created successfully!", extra_tags="add_announcement")

            # Send notifications to all officers except the one who updated the announcement
            officers = User.objects.filter(is_officer=True).exclude(id=creating_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"New announcement: {announcement.what} has been created by {creating_officer.fname} {creating_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            # Send notifications to all members
            members = User.objects.filter(is_member=True)
            for member in members:
                notification = Notification.objects.create(
                    recipient=member,  # Send notification to member
                    content=f"New announcement: {announcement.what}",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('create_announcement', username=username)
    else:
        form = AnnouncementForm()
    return render(request, 'officer/newsfeed/announcement_form.html', {'form': form})

@login_required
@user_passes_test(is_officer, login_url='/login')
def update_announcement(request, username, pk):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    announcement = Announcement.objects.get(pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            # Store the officer who is updating the announcement
            updating_officer = request.user
            
            # Save the updated announcement
            form.save()

            messages.success(request, "Announcement updated successfully!", extra_tags="update_announcement")

            # Send notifications to all officers except the one who updated the announcement
            officers = User.objects.filter(is_officer=True).exclude(id=updating_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to officer
                    content=f"Announcement: '{announcement.what}' has been updated by {updating_officer.fname} {updating_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            # Send notifications to all members
            members = User.objects.filter(is_member=True)
            for member in members:
                notification = Notification.objects.create(
                    recipient=member,  # Send notification to member
                    content=f"Announcement: '{announcement.what}' has been updated.",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('news_feed', username=username)
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'officer/newsfeed/announcement_form.html', {'form': form, 'announcement': announcement})

@login_required
@user_passes_test(is_officer, login_url='/login') 
def delete_announcement(request, username, pk):
    announcement = get_object_or_404(Announcement, pk=pk)  # Adjust as necessary based on your Note model structure
    if request.method == 'POST':
        announcement.delete()
        
        messages.success(request, "Announcement deleted successfully!", extra_tags="update_announcement")
        return redirect('news_feed', username=username)  # Redirect back to the landing page after deletion
    return redirect('news_feed', username=username)

#officer_views_household
class HouseholdListView(RoleRequiredMixin, ListView):
    allowed_roles = ['is_officer']
    model = Household
    template_name = 'officer/household/household_list.html'
    context_object_name = 'households'

    def dispatch(self, request, *args, **kwargs):
        # Check if the user's profile is updated
        if self.request.user.username != self.kwargs.get('username'):
            messages.error(self.request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
            
        if not request.user.fname or not request.user.lname:
            messages.warning(
                request, 
                "Update your profile first!", 
                extra_tags="officer_update_prof"
            )
            return redirect(reverse('officer_update_profile', kwargs={'username': request.user.username}))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Household.objects.prefetch_related('billings').annotate(
            number_of_residents=Count('residents')
        )

        # Handle search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(owner_name__fname__icontains=search_query) |
                Q(owner_name__lname__icontains=search_query) |
                Q(block__icontains=search_query) |
                Q(street__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'owner_name__fname')
        direction = self.request.GET.get('direction', 'asc')

        # Exclude overall_billing_status from the queryset sort
        if sort_by != 'overall_billing_status':
            order_by = sort_by if direction == 'asc' else f'-{sort_by}'
            queryset = queryset.order_by(order_by)

        return queryset

    def post(self, request, *args, **kwargs):
        billing_month = request.POST.get("billing_month")
        amount = request.POST.get("amount")
        
        # Modify billing_month to add the day part
        billing_month += "-01"  # Convert from YYYY-MM to YYYY-MM-DD format

        try:
            # Get the officer who added the billing
            adding_officer = request.user

            # Create billing for each household
            for household in Household.objects.all():
                Billing.objects.create(
                    household=household,
                    billing_month=billing_month,
                    amount=amount,
                    status="Unpaid",
                )
            # Send notifications to all users (members and officers) except the officer who added the billing
            users = User.objects.exclude(id=adding_officer.id)  # Exclude the officer who added the billing
            for user in users:
                # Create a notification for each user
                Notification.objects.create(
                    recipient=user,
                    content=f"New billing for {billing_month} has been added by Officer {adding_officer.fname} {adding_officer.lname}.",
                    created_at=timezone.now()
                )

            messages.success(request, "Monthly billing added for all households!", extra_tags="billing_added")
        except Exception as e:
            messages.error(request, "Billing already exist!", extra_tags="billing_added")

        return redirect(reverse('household_list', kwargs={'username': self.kwargs['username']}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get filtered and sorted queryset
        households_queryset = self.get_queryset()

        # Add pagination
        paginator = Paginator(households_queryset, 6)  # Show 6 households per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Calculate the overall billing status for each household on the current page
        for household in page_obj:
            billing_statuses = household.billings.values_list('status', flat=True)
            if not billing_statuses:
                household.overall_billing_status = 'Empty'
            elif 'Overdue' in billing_statuses:
                household.overall_billing_status = 'Overdue'
            elif 'Unpaid' in billing_statuses:
                household.overall_billing_status = 'Unpaid'
            else:
                household.overall_billing_status = 'Updated'

        # Handle sorting by overall billing status
        sort_by = self.request.GET.get('sort', 'owner_name__fname')
        direction = self.request.GET.get('direction', 'asc')
        if sort_by == 'overall_billing_status':
            page_obj.object_list = sorted(
                page_obj.object_list,
                key=lambda h: h.overall_billing_status,
                reverse=(direction == 'desc')
            )

        # Add context for pagination and sorting
        context['households'] = page_obj
        context['sort_by'] = sort_by
        context['direction'] = direction
        context['search_query'] = self.request.GET.get('search', '')

        return context

class ResidentListView(RoleRequiredMixin, ListView):
    allowed_roles = ['is_officer']
    model = Resident
    template_name = 'officer/household/resident_list.html'
    context_object_name = 'residents'

    def dispatch(self, request, *args, **kwargs):
        if request.user.username != kwargs.get('username'):
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')

        # Check if the user's profile is updated
        if not request.user.fname or not request.user.lname:
            messages.warning(
                request, 
                "Update your profile first!", 
                extra_tags="officer_update_prof"
            )
            return redirect(reverse('officer_update_profile', kwargs={'username': request.user.username}))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Start with the base queryset
        queryset = Resident.objects.all().select_related('household')

        # Handle search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(household__owner_name__lname__icontains=search_query) |
                Q(household__block__icontains=search_query) |
                Q(household__street__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'household')
        direction = self.request.GET.get('direction', 'asc')

        if sort_by == 'block':
            sort_by = 'household__block'
        elif sort_by == 'street':
            sort_by = 'household__street'
        elif sort_by == 'household':
            sort_by = 'household__owner_name__lname'
        elif sort_by == 'first_name':
            sort_by = 'first_name'
        elif sort_by == 'last_name':
            sort_by = 'last_name'

        if direction == 'desc':
            queryset = queryset.order_by(f'-{sort_by}')
        else:
            queryset = queryset.order_by(sort_by)

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get filtered and sorted queryset
        residents_queryset = self.get_queryset()

        # Add pagination
        paginator = Paginator(residents_queryset, 6)  # Show 6 residents per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Handle sorting by overall billing status
        sort_by = self.request.GET.get('sort', 'household')
        direction = self.request.GET.get('direction', 'asc')

        # Add context for pagination and sorting
        context['residents'] = page_obj
        context['sort_by'] = sort_by
        context['direction'] = direction
        context['search_query'] = self.request.GET.get('search', '')

        # Add household id for each resident
        context['household_ids'] = {resident.id: resident.household.id for resident in residents_queryset}

        return context

class HouseholdDetailView(RoleRequiredMixin, View):
    allowed_roles = ['is_officer']
    def get(self, request, username, pk):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        user = request.user
        household = get_object_or_404(Household, pk=pk)

        # Get all residents that belong to the household
        residents = Resident.objects.filter(household=household)

        # Get all billings related to the household
        billings = Billing.objects.filter(household=household).order_by('-billing_month')

        # Prepare the context with household, residents, and billing information
        context = {
            'household': household,
            'residents': residents,
            'billings': billings,
            'fields': [
                {'display_name': 'First Name'},
                {'display_name': 'Relation to Head'},
                {'display_name': 'Email'},
                {'display_name': 'Birth Date'},
                {'display_name': 'Contact Number'},
                {'display_name': 'Actions'},
            ]
        }

        return render(request, 'officer/household/view_household.html', context)

class EditHousehold(RoleRequiredMixin, View):
    allowed_roles = ['is_officer']
    def get(self, request, username, pk):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        household = get_object_or_404(Household, pk=pk)
        form = HouseholdForm(instance=household)
        return render(request, 'officer/household/edithousehold.html', {'form': form, 'household': household})

    def post(self, request, username, pk):
        household = get_object_or_404(Household, pk=pk)
        form = HouseholdForm(request.POST, instance=household)
        
        if form.is_valid():
            # Save the household form
            household = form.save()

            messages.success(request, "Household updated successfully!", extra_tags="household_officer_update")
            # Get the officer who is editing the household
            editing_officer = request.user
            
            # Get the member associated with the household
            member = household.owner_name  # Assuming 'owner_name' is the user who is the member

            # Create a notification for the member (who owns the household)
            notification = Notification.objects.create(
                recipient=member,  # Send notification to the member
                content=f"Your household details have been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                created_at=timezone.now()
            )
            notification.save()

            # Send notifications to all officers except the one who edited the household
            officers = User.objects.filter(is_officer=True).exclude(id=editing_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,  # Send notification to the officer
                    content=f"The details of household '{household.owner_name}' have been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()
            return redirect('view_household', username=username, pk=pk)
        
        return render(request, 'officer/household/edithousehold.html', {'form': form, 'household': household})

#officer_views_resident
class ViewResidentInfo(RoleRequiredMixin, View):
    allowed_roles = ['is_officer']
    def get(self, request, username, pk, resident_id):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        household = get_object_or_404(Household, pk=pk)
        resident = get_object_or_404(Resident, id=resident_id)
        return render(request, 'officer/household/view_resident_info.html', {'resident': resident, 'household': household})

class EditResident(RoleRequiredMixin, View):
    allowed_roles = ['is_officer']
    def get(self, request, username, pk, resident_id):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        household = get_object_or_404(Household, pk=pk)
        resident = get_object_or_404(Resident, id=resident_id)
        form = ResidentForm(instance=resident)
        context = {
        'form': form,
        'resident': resident,
        'household': household,
        'gender_choices': Resident.GENDER_CHOICES,
        'civil_status_choices': Resident.CIVIL_STATUS_CHOICES,
        'religion_choices': Resident.RELIGION_CHOICES,
        'educational_attainment_choices': Resident.EDUCATIONAL_ATTAINMENT_CHOICES,
        }

        return render(request, 'officer/household/editresident.html', context)

    def post(self, request, username, pk, resident_id):
        household = get_object_or_404(Household, pk=pk)
        resident = get_object_or_404(Resident, id=resident_id)
        form = ResidentForm(request.POST, instance=resident)
        
        if form.is_valid():
            # Save the form
            resident = form.save()

            messages.success(request, "Resident updated successfully!", extra_tags="resident_officer_update")
            # Get the officer who made the edit
            editing_officer = request.user

            member = household.owner_name

            # Send a notification to the household (connected resident)
            notification = Notification.objects.create(
                recipient=member,  # Assuming the notification relates to the household
                content=f"The details for resident {resident.first_name} {resident.last_name} have been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                created_at=timezone.now()
            )
            notification.save()

            # Send notifications to all other officers
            officers = User.objects.filter(is_officer=True).exclude(id=editing_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,
                    content=f"Resident details for {resident.first_name} {resident.last_name} have been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('view_resident_info', username=username, pk=household.id, resident_id=resident.id)
        else:
            form = ResidentForm(instance=resident)
        
        gender_choices = Resident.GENDER_CHOICES
        civil_status_choices = Resident.CIVIL_STATUS_CHOICES
        religion_choices = Resident.RELIGION_CHOICES
        educational_attainment_choices = Resident.EDUCATIONAL_ATTAINMENT_CHOICES

        return render(request, 'officer/household/editresident.html', {
            'form': form, 
            'resident': resident,
            'gender_choices': gender_choices,
            'civil_status_choices': civil_status_choices,
            'religion_choices': religion_choices,
            'educational_attainment_choices': educational_attainment_choices
        })

@login_required
@user_passes_test(is_officer, login_url='/login')
def dlt_resident(request, username, pk, resident_id):
    household = get_object_or_404(Household, pk=pk)
    resident = get_object_or_404(Resident, id=resident_id)

    if request.method == 'POST':
        # Get the officer who is performing the deletion
        deleting_officer = request.user

        member = household.owner_name
        # Send a notification to the household (connected resident)
        notification = Notification.objects.create(
            recipient=member,  # Notification is related to the household
            content=f"The details for resident {resident.first_name} {resident.last_name} have been removed from the household by Officer {deleting_officer.fname} {deleting_officer.lname}.",
            created_at=timezone.now()
        )
        notification.save()

        # Send notifications to all other officers
        officers = User.objects.filter(is_officer=True).exclude(id=deleting_officer.id)
        for officer in officers:
            notification = Notification.objects.create(
                recipient=officer,
                content=f"The details for resident {resident.first_name} {resident.last_name} have been removed from household {household.owner_name} by Officer {deleting_officer.fname} {deleting_officer.lname}.",
                created_at=timezone.now()
            )
            notification.save()

        # Delete the resident
        resident.delete()

        messages.success(request, "Resident deleted successfully!", extra_tags="household_officer_update")
        return redirect('view_household', username=username, pk=pk)
    else:
        messages.error(request, "Invalid request method.")
    return redirect('view_household', username=username, pk=pk)

#officer_views_billing
class edit_billing_status(RoleRequiredMixin, View):
    allowed_roles = ['is_officer']
    def get(self, request, username, pk, billing_id):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        household = get_object_or_404(Household, pk=pk)
        billing = get_object_or_404(Billing, id=billing_id)
        form = BillingStatusForm(instance=billing)
        return render(request, 'officer/household/edit_billing.html', {'form': form, 'billings': billing, 'household': household})

    def post(self, request, username, pk, billing_id):
        household = get_object_or_404(Household, pk=pk)
        billing = get_object_or_404(Billing, id=billing_id)
        form = BillingStatusForm(request.POST, instance=billing)

        if form.is_valid():
            # Get the officer who is making the change
            editing_officer = request.user

            # Save the form (which updates the billing status)
            billing = form.save()

            messages.success(request, "Billing updated successfully!", extra_tags="household_officer_update")
            # Create a notification for the household owner (member)
            member = household.owner_name  # The member (household owner) who will receive the notification
            notification = Notification.objects.create(
                recipient=member,  # Send to the household owner (member)
                content=f"Your billing status for household {household.owner_name} has been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                created_at=timezone.now()
            )
            notification.save()

            # Send notifications to other officers (excluding the officer who edited)
            officers = User.objects.filter(is_officer=True).exclude(id=editing_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,
                    content=f"The billing status for household {household.owner_name} has been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            # Redirect to the household view page after updating the billing status
            return redirect('view_household', username=username, pk=pk)

        return render(request, 'officer/household/edit_billing.html', {'form': form, 'billings': billing, 'household': household})

#officer_views_reservation
class ReservationListView(RoleRequiredMixin, ListView):
    allowed_roles = ['is_officer']
    model = Reservation
    template_name = 'officer/reservation/reservation_list.html'
    context_object_name = 'reservations'

    def dispatch(self, request, *args, **kwargs):
        if request.user.username != kwargs.get('username'):
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        # Check if the user's profile is updated
        if not request.user.fname or not request.user.lname:
            messages.warning(
                request, 
                "Update your profile first!", 
                extra_tags="officer_update_prof"
            )
            return redirect(reverse('officer_update_profile', kwargs={'username': request.user.username}))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(household__owner_name__fname__icontains=search_query) |
                Q(household__owner_name__lname__icontains=search_query) |
                Q(reservation_date__icontains=search_query) |
                Q(amenities__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

         # Add pagination
        reservations = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(reservations, 6)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['reservations'] = page_obj

        return context

@login_required
@user_passes_test(is_officer, login_url='/login')
def update_reservation_status(request, username, reservation_id):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    # Fetch the reservation instance or return a 404 error if not found
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        form = ReservationStatusForm(request.POST, instance=reservation)
        if form.is_valid():
            # Update the reservation status and set the officer flag
            updated_reservation = form.save(commit=False)
            updated_reservation.status_changed_by_officer = True
            updated_reservation.save()

            messages.success(request, "Reservation updated successfully!", extra_tags="reservation_officer_update")
            # Get the officer who updated the reservation
            updating_officer = request.user

            # Send a notification to the member who made the reservation (household owner)
            member = reservation.household.owner_name  # Adjust this if your model has a different relationship
            Notification.objects.create(
                recipient=member,  # Assuming you have a way to get the member from the reservation
                content=f"Your reservation for {reservation.amenities} has been {reservation.status} by Officer {updating_officer.fname} {updating_officer.lname}.",
                created_at=timezone.now()
            )

            # Send notifications to all officers (except the one who updated the reservation)
            officers = User.objects.filter(is_officer=True).exclude(id=updating_officer.id)
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,
                    content=f"Reservation of {member} for {reservation.amenities} has been {reservation.status} by Officer {updating_officer.fname} {updating_officer.lname}.",
                    created_at=timezone.now()
                )

            messages.success(request, "Reservation status updated successfully!")
            return redirect('reservation_list', username=request.user.username)
    else:
        form = ReservationStatusForm(instance=reservation)

    return render(request, 'officer/reservation/update_reservation.html', {
        'form': form,
        'reservation': reservation,
    })

#officer_views_request
class RequestListView(RoleRequiredMixin, ListView):
    allowed_roles = ['is_officer']
    model = ServiceRequest
    template_name = 'officer/services/request_list.html'
    context_object_name = 'servicerequests'

    def dispatch(self, request, *args, **kwargs):
        if request.user.username != kwargs.get('username'):
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        # Check if the user's profile is updated
        if not request.user.fname or not request.user.lname:
            messages.warning(
                request, 
                "Update your profile first!", 
                extra_tags="officer_update_prof"
            )
            return redirect(reverse('officer_update_profile', kwargs={'username': request.user.username}))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(household__owner_name__fname__icontains=search_query) |
                Q(household__owner_name__lname__icontains=search_query) |
                Q(service_type__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(updated_at__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

        servicerequests = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(servicerequests, 6)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['servicerequests'] = page_obj

        return context

class ViewRequest(RoleRequiredMixin, View):
    allowed_roles = ['is_officer']
    def get(self, request, username, request_id):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        servicerequest = get_object_or_404(ServiceRequest, id=request_id)
        return render(request, 'officer/services/view_request.html', {'servicerequest': servicerequest})

@login_required
@user_passes_test(is_officer, login_url='/login')
def update_request_status(request, username, servicerequest_id):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    # Fetch the service request instance or return a 404 error if not found
    servicerequest = get_object_or_404(ServiceRequest, id=servicerequest_id)

    if request.method == 'POST':
        form = ServiceRequestStatusForm(request.POST, instance=servicerequest)
        if form.is_valid():
            # Update the service request status and set the officer flag
            updated_request = form.save(commit=False)
            updated_request.status_changed_by_officer = True
            updated_request.save()

            messages.success(request, "Request updated successfully!", extra_tags="request_officer_update")
            # Get the officer who updated the service request
            updating_officer = request.user

            # Send a notification to the member who made the service request (household owner)
            member = servicerequest.household.owner_name  # Adjust this if your model has a different relationship
            Notification.objects.create(
                recipient=member,  # Assuming you have a way to get the member from the service request
                content=f"Your {servicerequest.service_type} has been updated by Officer {updating_officer.fname} {updating_officer.lname}.",
                created_at=timezone.now()
            )

            # Send notifications to all officers (except the one who updated the service request)
            officers = User.objects.filter(is_officer=True).exclude(id=updating_officer.id)
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,
                    content=f"{servicerequest.service_type} of {member} has been updated by Officer {updating_officer.fname} {updating_officer.lname}.",
                    created_at=timezone.now()
                )

            messages.success(request, "Service request status updated successfully!")
            return redirect('request_list', username=request.user.username)
    else:
        form = ServiceRequestStatusForm(instance=servicerequest)

    return render(request, 'officer/services/update_request.html', {
        'form': form,
        'servicerequest': servicerequest,
    })

#officer_views_appointment
class AppointmentListView(RoleRequiredMixin, ListView):
    allowed_roles = ['is_officer']
    model = GrievanceAppointment
    template_name = 'officer/grievance/appointment_list.html'
    context_object_name = 'grievance_appointments'

    def dispatch(self, request, *args, **kwargs):
        if request.user.username != kwargs.get('username'):
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        # Check if the user's profile is updated
        if not request.user.fname or not request.user.lname:
            messages.warning(
                request, 
                "Update your profile first!", 
                extra_tags="officer_update_prof"
            )
            return redirect(reverse('officer_update_profile', kwargs={'username': request.user.username}))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        # Handle search query
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(household__owner_name__fname__icontains=search_query) |
                Q(household__owner_name__lname__icontains=search_query) |
                Q(appointment_type__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(reservation_date__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Handle sorting
        sort_by = self.request.GET.get('sort', 'updated_at')  # Default sort field
        direction = self.request.GET.get('direction', 'desc')  # Default direction
        order_by = sort_by if direction == 'asc' else '-' + sort_by

        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the search query and sorting parameters
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', 'updated_at')
        direction = self.request.GET.get('direction', 'desc')

        context['search_query'] = search_query
        context['sort_by'] = sort_by
        context['direction'] = direction

        grievance_appointments = self.get_queryset()  # Get filtered and sorted reservations
        paginator = Paginator(grievance_appointments, 6)  # Show 6 reservations per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['grievance_appointments'] = page_obj

        return context

class ViewAppointment(RoleRequiredMixin, View):
    allowed_roles = ['is_officer']
    def get(self, request, username, request_id):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        grievanceappointment = get_object_or_404(GrievanceAppointment, id=request_id)
        return render(request, 'officer/grievance/view_appointment.html', {'grievanceappointment': grievanceappointment})

@login_required
@user_passes_test(is_officer, login_url='/login')
def update_appointment_status(request, username, grievanceappointment_id):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    # Fetch the grievance appointment instance or return a 404 error if not found
    grievance_appointment = get_object_or_404(GrievanceAppointment, id=grievanceappointment_id)

    if request.method == 'POST':
        form = GrievanceStatusForm(request.POST, instance=grievance_appointment)
        if form.is_valid():
            # Update the grievance appointment status and set the officer flag
            updated_appointment = form.save(commit=False)
            updated_appointment.status_changed_by_officer = True
            updated_appointment.save()

            messages.success(request, "Appointment updated successfully!", extra_tags="appointment_officer_update")
            # Get the officer who updated the grievance appointment
            updating_officer = request.user

            # Send a notification to the member who made the grievance appointment (household owner)
            member = grievance_appointment.household.owner_name  # Adjust this if your model has a different relationship
            Notification.objects.create(
                recipient=member,  # Assuming you have a way to get the member from the grievance appointment
                content=f"Your appointment for {grievance_appointment.appointment_type} has been updated by Officer {updating_officer.fname} {updating_officer.lname}.",
                created_at=timezone.now()
            )

            # Send notifications to all officers (except the one who updated the grievance appointment)
            officers = User.objects.filter(is_officer=True).exclude(id=updating_officer.id)
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,
                    content=f"Appointment of {member} for {grievance_appointment.appointment_type} has been updated by Officer {updating_officer.fname} {updating_officer.lname}.",
                    created_at=timezone.now()
                )

            messages.success(request, "Grievance appointment status updated successfully!")
            return redirect('appointment_list', username=request.user.username)
    else:
        form = GrievanceStatusForm(instance=grievance_appointment)

    return render(request, 'officer/grievance/update_appointment.html', {
        'form': form,
        'grievance_appointment': grievance_appointment,
    })

# Officer User Management View
@login_required
@user_passes_test(is_officer, login_url='/login')
def manage_users(request, username):
    if request.user.username != username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = request.user
    # Check if the user's profile is updated
    if not user.fname or not user.lname:
        messages.warning(request, "Update your profile first!", extra_tags="officer_update_prof")
        return redirect('officer_update_profile', username=request.user.username)  # Redirect to profile update page
        
    # Get search query from request
    search_query = request.GET.get('search', '')

    # Fetch all users except superadmins (is_superuser=False)
    users = User.objects.filter(is_superuser=False)

    # If there's a search query, filter the users accordingly
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(fname__icontains=search_query) |
            Q(lname__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Get sorting criteria from query parameters
    sort_by = request.GET.get('sort', 'date_joined')  # Default sort by `date_joined`
    direction = request.GET.get('direction', 'desc')  # Default direction is descending

    # Sort users based on the selected column and direction
    if sort_by == 'role':
        # Custom sorting for role (is_officer, is_member)
        users = sorted(users, key=lambda u: (u.is_officer, u.is_member), reverse=(direction == 'desc'))
    elif sort_by == 'status':
        users = users.order_by('is_active' if direction == 'asc' else '-is_active')
    elif sort_by == 'date_joined':
        users = users.order_by('date_joined' if direction == 'asc' else '-date_joined')
    else:
        users = users.order_by(sort_by if direction == 'asc' else f'-{sort_by}')

    # Paginate the results
    paginator = Paginator(users, 6)  # Show 6 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prepare context for the template
    context = {
        'users': page_obj,
        'sort_by': sort_by,
        'direction': direction,
        'search_query': search_query,
    }

    return render(request, 'officer/usermgt/manage_users.html', context)

@login_required
@user_passes_test(is_officer, login_url='/login')
def toggle_user_activation(request, username, user_id):
    user = get_object_or_404(User, id=user_id)

    # Check if the user making the request is an officer
    if request.user.is_officer:
        # Toggle the user's active status
        previous_status = user.is_active
        user.is_active = not user.is_active
        user.save()

        # Create a notification for the user whose account was toggled
        action = "activated" if user.is_active else "deactivated"
        Notification.objects.create(
            recipient=user,
            content=f"Your account has been {action} by Officer {request.user.fname} {request.user.lname}.",
            created_at=timezone.now()
        )

        # Optionally, add a success message to the request
        messages.success(request, f"User {user.fname} {user.lname} has been {action}!", extra_tags="user_message")

    # Redirect to the manage_users view using the officer's username
    return redirect('manage_users', username=request.user.username)

@login_required
@user_passes_test(is_officer, login_url='/login')
def delete_user(request, username, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Save the deleted user's name for notification content
        deleted_user_name = f"{user.fname} {user.lname}"
        
        # Delete the user
        user.delete()

        messages.success(request, f"User {deleted_user_name} has been deleted successfully!", extra_tags="user_message")
        # Notify all officers except the one performing the deletion
        officers = User.objects.filter(is_officer=True).exclude(id=request.user.id)
        for officer in officers:
            Notification.objects.create(
                recipient=officer,
                content=f"Officer {request.user.fname} {request.user.lname} deleted the account of {deleted_user_name}.",
                created_at=timezone.now()
            )

        # Redirect to manage users page
        return redirect('manage_users', username=username)

    return redirect('manage_users', username=username)

#officer_views_profile
@login_required
@user_passes_test(is_officer, login_url='/login')
def officer_profile_info(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = request.user
    return render(request, 'officer/profile/profile_info.html', {
        'user': user
    })

@login_required
@user_passes_test(is_officer, login_url='/login')
def officer_update_profile(request, username):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = User.objects.get(username=username)
    assigned_roles = Officer.objects.exclude(user=user).values_list('officer_position', flat=True)
    available_roles_choices = [choice for choice in Officer.ROLES_CHOICES if choice[0] not in assigned_roles]

    if request.method == 'POST':
        form = OfficerChangeForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            # Get the new username from the form
            new_username = form.cleaned_data.get('username')

            # Check for duplicate username only if it has been changed
            if new_username and new_username != username and User.objects.filter(username=new_username).exists():
                messages.error(request, "The username you entered is already taken.")
                return render(request, 'officer/profile/profile_update.html', {
                    'form': form,
                    'roles_choices': available_roles_choices
                })

            user = form.save(commit=False)
            
            # Update username_changed timestamp when username is changed
            if user.username != username:
                user.username_changed = timezone.now()
            
            user.save()

            messages.success(request, "Profile updated successfully!", extra_tags="profile_updated")
            return redirect('officer_profile_info', username=user.username)
    else:
        form = OfficerChangeForm(instance=user)

    return render(request, 'officer/profile/profile_update.html', {
        'form': form,
        'roles_choices': available_roles_choices
    })

@login_required
@user_passes_test(is_officer, login_url='/login')
def officer_delete_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')
    else:
        messages.error(request, "Invalid request.")
        return redirect('officer_delete_profile', username=request.user.username)

#officer_views_calendar
@login_required
@user_passes_test(is_officer, login_url='/login')
def events_calendar(request, username, year=None, month=None):
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    user = request.user
    
    # Check if the user's profile is updated
    if not user.fname or not user.lname:
        messages.warning(request, "Update your profile first!", extra_tags="officer_update_prof")
        return redirect('officer_update_profile', username=request.user.username)  # Redirect to profile update page

    today = date.today()

    # Check if a month is selected from the input form
    selected_month_str = request.GET.get('selected_month')
    if selected_month_str:
        # Parse the selected month (format YYYY-MM) to set year and month
        selected_date = datetime.strptime(selected_month_str, "%Y-%m")
        year = selected_date.year
        month = selected_date.month
    elif year is None or month is None:
        year = today.year
        month = today.month
    else:
        year = int(year)
        month = int(month)

    # The rest of the logic remains the same as before.
    month_calendar = get_month_calendar(year, month)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    current_month = date(year, month, 1)
    prev_month_name = (date(year, prev_month, 1)).strftime('%B')
    next_month_name = (date(year, next_month, 1)).strftime('%B')

    context = {
        'calendar': month_calendar,
        'year': year,
        'month': current_month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'prev_month_name': prev_month_name,
        'next_month_name': next_month_name,
    }

    return render(request, 'officer/events/calendar.html', context)

#officer_views_reports
@login_required
@user_passes_test(is_officer, login_url='/login')
def upload_financial_file(request, username):
    # Ensure the username in the URL matches the logged-in user
    if username != request.user.username:
        messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
        return redirect('login')
    
    user = request.user

    # Check if the user's profile is updated
    if not user.fname or not user.lname:
        messages.warning(request, "Update your profile first!", extra_tags="officer_update_prof")
        return redirect('officer_update_profile', username=request.user.username)

    if request.method == 'POST':
        form = FinancialFileForm(request.POST, request.FILES)
        if form.is_valid():
            creating_officer = request.user
            financial_file = form.save(commit=False)
            financial_file.uploaded_by = creating_officer
            financial_file.save()

            messages.success(request, 'File uploaded successfully!', extra_tags="file_upload")

            # Notify all officers except the uploading officer
            officers = User.objects.filter(is_officer=True).exclude(id=creating_officer.id)
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,
                    content=f"New Financial Statement: {financial_file.title} has been uploaded by {creating_officer.fname} {creating_officer.lname}.",
                    created_at=timezone.now()
                )

            # Notify all members
            members = User.objects.filter(is_member=True)
            for member in members:
                Notification.objects.create(
                    recipient=member,
                    content=f"New Financial Statement: {financial_file.title} is now available.",
                    created_at=timezone.now()
                )

            return redirect('upload_financial_file', username=request.user.username)
        else:
            messages.error(request, 'File upload failed! Please check the form and try again.')

    else:
        form = FinancialFileForm()

    # Retrieve all financial files
    files = FinancialFile.objects.all()

    # Get search query from request
    search_query = request.GET.get('search', '')
    if search_query:
        files = files.filter(
            Q(title__icontains=search_query) |
            Q(uploaded_at__icontains=search_query)
        )

    # Get sorting criteria from query parameters
    sort_by = request.GET.get('sort', 'uploaded_at')  # Default sort by `uploaded_at`
    direction = request.GET.get('direction', 'desc')  # Default direction is descending

    # Sort files based on the selected column and direction
    if sort_by in ['title', 'uploaded_at']:
        files = files.order_by(f"{'' if direction == 'asc' else '-'}{sort_by}")
    else:
        files = files.order_by('-uploaded_at')  # Default fallback sorting

    # Paginate the results
    paginator = Paginator(files, 6)  # Show 6 files per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prepare context for the template
    context = {
        'form': form,
        'files': page_obj,
        'sort_by': sort_by,
        'direction': direction,
        'search_query': search_query,
    }

    return render(request, 'officer/upload_financial_file.html', context)

@login_required
@user_passes_test(is_officer, login_url='/login')
def dl_file(request, username, file_id):
    # Get the financial file object
    financial_file = get_object_or_404(FinancialFile, id=file_id)

    # Get the Cloudinary file URL
    file_url = financial_file.file.url  # Cloudinary URL for the file

    # Download the file content from Cloudinary
    file_content = requests.get(file_url).content

    # Create a response to serve the file with the correct MIME type
    response = HttpResponse(file_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{financial_file.file.public_id.split("/")[-1]}"'
    return response
    
@login_required
@user_passes_test(is_officer, login_url='/login')
def delete_file(request, username, file_id):
    file = get_object_or_404(FinancialFile, id=file_id)

    if request.method == "POST":
        file.delete()
        messages.success(request, 'File deleted successfully!', extra_tags="file_upload")
        return redirect('upload_financial_file', username=request.user.username)

    messages.error(request, "Invalid request.")
    return redirect('upload_financial_file', username=request.user.username)

#officer_views_notif
class OfficerNotificationsView(RoleRequiredMixin, View):
    allowed_roles = ['is_officer']
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(recipient=request.user).all()

        return render(request, 'officer/officer_sidebar.html', {
            'notifications': notifications
        })

@login_required
def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, recipient=request.user)
    notification.read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def mark_all_as_read(request):
    # Update all notifications for the logged-in user to mark them as read
    Notification.objects.filter(recipient=request.user, read=False).update(read=True)
    return redirect(request.META.get('HTTP_REFERER', '/'))

class ViewUserInfo(RoleRequiredMixin, View):
    allowed_roles = ['is_officer']
    def get(self, request, username, user_id):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        user_prof = get_object_or_404(User, id=user_id)
        return render(request, 'officer/usermgt/user_profile.html', {'user_prof': user_prof})

class EditUserInfo(RoleRequiredMixin, View):
    allowed_roles = ['is_officer']
    def get(self, request, username, user_id):
        if username != request.user.username:
            messages.error(request, "You are not authorized to access this page.", extra_tags="unauthorized")
            return redirect('login')
        user_prof = get_object_or_404(User, id=user_id)
        form = OfficerChangeForm(instance=user_prof)
        assigned_roles = Officer.objects.exclude(user=user_prof).values_list('officer_position', flat=True)
        available_roles_choices = [choice for choice in Officer.ROLES_CHOICES if choice[0] not in assigned_roles]
        context = {
        'user_prof': user_prof,
        'form': form,
        'roles_choices': available_roles_choices
        }

        return render(request, 'officer/usermgt/update_user_prof.html', context)

    def post(self, request, username, user_id):
        user_prof = get_object_or_404(User, id=user_id)
        form = OfficerChangeForm(request.POST, request.FILES, instance=user_prof)
        
        if form.is_valid():
            # Save the form
            user_prof = form.save()

            messages.success(request, "User updated successfully!", extra_tags="user_officer_update")
            # Get the officer who made the edit
            editing_officer = request.user

            # Send a notification to the household (connected resident)
            notification = Notification.objects.create(
                recipient=user_prof,  # Assuming the notification relates to the household
                content=f"Your profile has been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                created_at=timezone.now()
            )
            notification.save()

            # Send notifications to all other officers
            officers = User.objects.filter(is_officer=True).exclude(id=editing_officer.id)
            for officer in officers:
                notification = Notification.objects.create(
                    recipient=officer,
                    content=f"User profile of {user_prof.fname} {user_prof.fname} have been updated by Officer {editing_officer.fname} {editing_officer.lname}.",
                    created_at=timezone.now()
                )
                notification.save()

            return redirect('user_profile', username=username, user_id=user_prof.id)
        else:
            form = OfficerChangeForm(instance=user_prof)
        
        assigned_roles = Officer.objects.exclude(user=user_prof).values_list('officer_position', flat=True)
        available_roles_choices = [choice for choice in Officer.ROLES_CHOICES if choice[0] not in assigned_roles]

        return render(request, 'officer/usermgt/update_user_prof.html', {
            'user_prof': user_prof,
            'form': form,
            'roles_choices': available_roles_choices
        })