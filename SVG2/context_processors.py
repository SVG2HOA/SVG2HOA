from .models import Notification, Household, User, GrievanceAppointment, ServiceRequest, Reservation, Announcement, Newsfeed, Member, Officer, Resident

def notifications_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user)
    else:
        notifications = []
    return {"notifications": notifications}

def unread_notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(recipient=request.user, read=False).count()
    else:
        unread_count = 0
    return {'unread_count': unread_count}