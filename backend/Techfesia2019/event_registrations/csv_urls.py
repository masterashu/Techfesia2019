from django.urls import path
from . import csv_views

urlpatterns = [
    path('event/<str:public_id>/registrations/', csv_views.get_event_registrations, name='event_registrations_csv'),
    path('login/', csv_views.staff_login, name='staff_login_csv')
]
