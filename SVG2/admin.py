from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Member, Officer, Household, Resident, Reservation, ServiceRequest, Billing, Newsfeed, NewsletterSubscriber, ContactSender, Announcement, GrievanceAppointment, Notification, FinancialFile, Term, EmergencyHotline, ElectionSession, Candidate, Vote


admin.site.register(User, UserAdmin)
class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ['pk', 'username', 'fname', 'lname', 'email', 'is_staff', 'is_member', 'is_officer', 'phone_number', 'profile_picture', 'proof_of_membership']
    readonly_fields = ('proof_of_membership',)

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('is_member', 'is_officer')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
            (None, {'fields': ('is_member', 'is_officer')}),
    )

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [ 'pk', 'user', 'user_info', 'fname', 'lname', 'email', 'phone_number', 'profile_picture']
    def user_info(self, obj):
        return obj.user.username
    user_info.short_description = 'Username'
    def fname(self, obj):
        return obj.user.fname
    def lname(self, obj):
        return obj.user.lname
    def email(self, obj):
        return obj.user.email
    def phone_number(self, obj):
        return obj.user.phone_number
    def profile_picture(self, obj):
        return obj.user.profile_picture

@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'pos', 'user_info', 'fname', 'lname', 'email', 'phone_number', 'profile_picture']
    def pos(self, obj):
        return obj.officer_position
    def user_info(self, obj):
        return obj.user.username
    user_info.short_description = 'Username'
    def fname(self, obj):
        return obj.user.fname
    def lname(self, obj):
        return obj.user.lname
    def email(self, obj):
        return obj.user.email
    def phone_number(self, obj):
        return obj.user.phone_number
    def profile_picture(self, obj):
        return obj.user.profile_picture

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ['pk', 'owner_name', 'block', 'street']
    ordering = ['pk', 'owner_name', 'block', 'street']

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'household', 'first_name', 'last_name']
    ordering = ['household']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'household', 'created_at', 'updated_at', 'reservation_date', 'amenities']
    ordering = ['pk', 'household', 'created_at', 'updated_at', 'reservation_date', 'amenities']

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['pk', 'household', 'service_type', 'street', 'created_at', 'updated_at', 'status', 'image']
    ordering = ['pk', 'household', 'street', 'service_type', 'created_at', 'updated_at', 'status']

@admin.register(GrievanceAppointment)
class GrievanceAppointmentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'household', 'appointment_type', 'subject', 'created_at', 'updated_at', 'reservation_date',  'status', 'image']
    ordering = ['pk', 'household', 'appointment_type', 'subject', 'created_at', 'updated_at', 'reservation_date', 'status']

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ['pk', 'household', 'billing_month', 'status']
    ordering = ['pk', 'household', 'billing_month', 'status']

@admin.register(Newsfeed)
class NewsfeedAdmin(admin.ModelAdmin):
    list_display = ['pk', 'written_by', 'pos', 'title', 'created_at', 'updated_at', 'image']
    ordering = ['pk', 'written_by', 'created_at']
    def pos(self, obj):
        return obj.written_by.officer_profile.officer_position

@admin.register(FinancialFile)
class FinancialFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'uploaded_by', 'file_size')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('who', 'what', 'date', 'time', 'where', 'image')

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(EmergencyHotline)
class EmergencyHotlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'number')

@admin.register(ElectionSession)
class ElectionSessionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'start_date', 'end_date', 'is_open')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'election')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'voter', 'election', 'submitted_at')


admin.site.register(NewsletterSubscriber)
admin.site.register(ContactSender)
admin.site.register(Notification)