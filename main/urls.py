from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Auth
    path('portal/login/', views.portal_login, name='login'),
    path('portal/logout/', views.portal_logout, name='logout'),

    # Customer portal
    path('portal/', views.dashboard, name='dashboard'),
    path('portal/archive/', views.ticket_archive, name='ticket_archive'),
    path('portal/tickets/new/', views.ticket_new, name='ticket_new'),
    path('portal/tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('portal/password/', views.portal_change_password, name='portal_change_password'),

    # Staff panel
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/archive/', views.staff_archive, name='staff_archive'),
    path('staff/tickets/<int:ticket_id>/', views.staff_ticket_detail, name='staff_ticket_detail'),
    path('staff/tickets/<int:ticket_id>/close/', views.staff_close_ticket, name='staff_close_ticket'),
    path('staff/tickets/<int:ticket_id>/reopen/', views.staff_reopen_ticket, name='staff_reopen_ticket'),
    path('staff/leads/', views.staff_leads, name='staff_leads'),
    path('staff/leads/<int:lead_id>/toggle/', views.staff_toggle_lead, name='staff_toggle_lead'),
    path('staff/clients/',        views.staff_clients,       name='staff_clients'),
    path('staff/clients/new/',    views.staff_client_create, name='staff_client_create'),
    path('staff/clients/<int:pk>/', views.staff_client_detail, name='staff_client_detail'),
]