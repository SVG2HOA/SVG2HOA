from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import LoginSignupView, member_landing_page, officer_landing_page, edit_household, add_household, add_resident, resident_detail, edit_resident, logout_view, make_reservation, ReservationListView, update_reservation_status, cancel_reservation, cancel_request, ViewAppointment, update_appointment_status
from .views import HouseholdListView, ResidentListView, HouseholdDetailView, HouseholdDetailsView, EditHousehold, submit_request, update_request, edit_billing_status, EditResident, ViewResidentInfo, newsfeed, news_feed, add_news, edit_news, RequestListView, update_request_status, AppointmentListView, calendar
from .views import subscribe_newsletter, events_calendar, eventscalendar, news_article, officer_profile_info, officer_update_profile, about, member_profile_info, member_update_profile, communitymap, MyReservation, MyRequest, ViewRequest, MyAppointment, make_appointment, cancel_appointment, update_appointment, update_reservation
from .views import OfficerNotificationsView, MemberNotificationsView, create_payment_link, send_activation_email
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name="home"),
    path('news/', views.news, name="news"),
    path('calendar/', calendar, name='calendar'),
    path('calendar/<int:year>/<int:month>/', calendar, name='calendar_with_date'),
    path('news-article/<int:pk>', views.news_article, name="news_article"),
    path('about/', views.about, name="about"),
    path('community-map/', communitymap, name="communitymap"),
    path('subscribed/', subscribe_newsletter, name='subscribe_newsletter'),
    path('login/', LoginSignupView.as_view(), name='login'),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),

#views for members
    path('<username>/dashboard/',  views.member_landing_page, name='member_landing_page'),
    path('<username>/dashboard/delete_note/<int:note_id>/', views.delete_note, name='delete_note'),
    #member newsfeed
    path('<username>/newsfeed', views.newsfeed, name='newsfeed'),
    path('<username>/newsfeed/article/<int:pk>', views.newsarticle, name="newsarticle"),
    #member household
    path('<username>/household/', HouseholdDetailsView.as_view(), name='household_detail'),
    path('<username>/household/edit/', edit_household.as_view(), name='edit_household'),
    path('<username>/household/add/', views.add_household, name='add_household'),
    #member residents
    path('<username>/household/residents/add/', views.add_resident, name='add_resident'),
    path('<username>/household/residents/<int:pk>/edit/', views.edit_resident, name='edit_resident'),
    path('<username>/household/residents/<int:pk>/delete/', views.delete_resident, name='delete_resident'),
    path('<username>/household/residents/<int:pk>/', views.resident_detail, name='resident_detail'),
    #member reservation
    path('<username>/reservations/make-a-reservation', views.make_reservation, name='make_reservation'),
    path('<username>/reservations/', MyReservation.as_view(), name='my_reservation'),
    path('<username>/reservation/update/<int:request_id>/', update_reservation, name='update_reservation'),
    path('<username>/reservation/cancel/<int:request_id>/', cancel_reservation, name='cancel_reservation'),
    #member request
    path('<username>/requests/submit-request', submit_request, name='submit_request'),
    path('<username>/requests/', MyRequest.as_view(), name='my_request'),
    path('<username>/request/update/<int:request_id>/', update_request, name='update_request'),
    path('<username>/request/cancel/<int:request_id>/', cancel_request, name='cancel_request'),
    #member appointment
    path('<username>/appointments/', MyAppointment.as_view(), name='my_appointment'),
    path('<username>/appointments/make-appointment', make_appointment, name='make_appointment'),
    path('<username>/appointment/update/<int:request_id>/', update_appointment, name='update_appointment'),
    path('<username>/appointment/cancel/<int:request_id>/', cancel_appointment, name='cancel_appointment'),
    #member calendar
    path('<username>/events_calendar/', views.eventscalendar, name='eventscalendar'),
    path('<username>/events_calendar/<int:year>/<int:month>/', eventscalendar, name='caldate'),
    #member profile
    path('<username>/profile/', member_profile_info, name='member_profile_info'),
    path('<username>/profile/update', member_update_profile, name='member_update_profile'),
    path('<int:pk>/profile/delete/', views.member_delete_profile, name='member_delete_profile'),
    #member notificatons
    path('<username>/dashboard/', MemberNotificationsView.as_view(), name='MemberNotificationsView'),
    #member financial report
    path('<username>/financial-statements/', views.financial_status, name='financial_status'),
    path('<username>/financial-statements/download/<int:file_id>/', views.download_file, name='download_file'),

#views for officers
    path('officer/<username>/dashboard/',  views.officer_landing_page, name='officer_landing_page'),
    #officer newsfeed
    path('officer/<username>/newsfeed/', views.news_feed, name='news_feed'),
    path('officer/<username>/newsfeed/add/', views.add_news, name='add_news'),
    path('officer/<username>/newsfeed/<int:pk>/edit/', views.edit_news, name='edit_news'),
    path('officer/<username>/newsfeed/delete-news/<int:pk>/', views.delete_news, name='delete_news'),
    path('officer/<username>/newsfeed/create-announcement/', views.create_announcement, name='create_announcement'),
    path('officer/<username>/newsfeed/update-announcement/<int:pk>/', views.update_announcement, name='update_announcement'),
    path('officer/<username>/newsfeed/delete-announcement/<int:pk>/', views.delete_announcement, name='delete_announcement'),
    path('officer/<username>/newsfeed/news-article/<int:pk>', views.news_single, name="news_single"),
    #officer household
    path('officer/<username>/household-list/', HouseholdListView.as_view(), name='household_list'),
    path('officer/<username>/resident-list/', ResidentListView.as_view(), name='resident_list'),
    path('officer/<username>/household-list/<int:pk>/', HouseholdDetailView.as_view(), name='view_household'),
    path('officer/<username>/household-list/<int:pk>/edit/', EditHousehold.as_view(), name='modify_household'),
    path('officer/<username>/household-list/<int:pk>/residents/<int:resident_id>', ViewResidentInfo.as_view(), name='view_resident_info'),
    path('officer/<username>/household-list/<int:pk>/residents/<int:resident_id>/edit/', EditResident.as_view(), name='edit_resident_info'),
    path('officer/<username>/household-list/<int:pk>/delete-resident/<int:resident_id>', views.dlt_resident, name='dlt_resident'),
    path('officer/<username>/household-list/<int:pk>/billing/<int:billing_id>/edit/', edit_billing_status.as_view(), name='edit_billing_status'),
    #officer reservation
    path('officer/<username>/reservation-list/', ReservationListView.as_view(), name='reservation_list'),
    path('officer/<username>/reservations/update-status/<int:reservation_id>/status/', update_reservation_status, name='update_reservation_status'),
    #officer request
    path('officer/<username>/service-request-list/', RequestListView.as_view(), name='request_list'),
    path('officer/<username>/service-request-list/view/<int:request_id>/', ViewRequest.as_view(), name='view_request'),
    path('officer/<username>/service-request/update-status/<int:servicerequest_id>/status/', update_request_status, name='update_request_status'),
    #officer profile
    path('officer/<username>/profile/', officer_profile_info, name='officer_profile_info'),
    path('officer/<username>/profile/update', officer_update_profile, name='officer_update_profile'),
    path('officer/<int:pk>/profile/delete/', views.officer_delete_profile, name='officer_delete_profile'),
    #officer appointment
    path('officer/<username>/appointment-list/', AppointmentListView.as_view(), name='appointment_list'),
    path('officer/<username>/appointment-list/view/<int:request_id>/', ViewAppointment.as_view(), name='view_appointment'),
    path('officer/<username>/appointment-list/update-status/<int:grievanceappointment_id>/status/', update_appointment_status, name='update_appointment_status'),
    #officer user management
    path('officer/<username>/manage_users/', views.manage_users, name='manage_users'),
    path('officer/<username>/manage_users/delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('officer/<username>/manage_users/toggle_user_activation/<int:user_id>/', views.toggle_user_activation, name='toggle_user_activation'),
    #officer events calendar
    path('officer/<username>/events_calendar/', views.events_calendar, name='events_calendar'),
    path('officer/<username>/events_calendar/<int:year>/<int:month>/', events_calendar, name='cal_w_date'),
    #officer notifications
    path('officer/<username>/dashboard/', OfficerNotificationsView.as_view(), name='OfficerNotificationsView'),
    path('mark_as_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('mark_all_as_read/', views.mark_all_as_read, name='mark_all_as_read'),
    #officer financial report
    path('officer/<username>/financial-statements/', views.upload_financial_file, name='upload_financial_file'),
    path('officer/<username>/financial-statements/download/<int:file_id>/', views.dl_file, name='dl_file'),
    path('officer/<username>/financial-statements/delete/<int:file_id>/', views.delete_file, name='delete_file'),

    path("<username>/household/billing/<int:billing_id>/", create_payment_link, name="create_payment_link"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)