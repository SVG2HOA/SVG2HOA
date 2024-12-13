from django.utils.timezone import now
from datetime import timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Reservation, Notification, User, Household, Resident, GrievanceAppointment, ServiceRequest, Member, Officer, Billing, Announcement, Newsfeed

# Utility function to create a notification if it doesn't already exist
def create_notification_if_not_exists(household, content, related_model, related_id, recipient_user=None):
    # Check if the notification already exists for the given model and ID
    if not Notification.objects.filter(
        household=household, 
        content=content, 
        related_model=related_model, 
        related_id=related_id
    ).exists():
        # If it doesn't exist, create it
        notification = Notification.objects.create(
            household=household,
            content=content,
            related_model=related_model,
            related_id=related_id
        )
        # If a recipient_user is provided, link the notification to that user
        if recipient_user:
            notification.user = recipient_user
            notification.save()

