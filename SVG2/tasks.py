# myapp/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Household, Billing

@shared_task
def create_monthly_billings():
    households = Household.objects.all()
    current_month = timezone.now().date().replace(day=1)  # Get the first day of the current month
    for household in households:
        # Create billing for the household for the current month if it doesn't exist
        Billing.objects.get_or_create(
            household=household,
            billing_month=current_month,
            defaults={'amount': 0.00, 'status': 'Unpaid'}  # Adjust the default amount as necessary
        )
