from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import *
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff, login_url='login')


# ---------------------------------------------------------------
# Public views
# ---------------------------------------------------------------

def home(request):
    return render(request, 'public/home.html')


def about(request):
    return render(request, 'public/about.html')


def contact(request):
    if request.method == 'POST':
        Lead.objects.create(
            name=request.POST['name'],
            company=request.POST.get('company', ''),
            email=request.POST['email'],
            phone=request.POST.get('phone', ''),
            service=request.POST.get('service', ''),
            message=request.POST['message'],
        )
        return render(request, 'public/contact.html', {'success': True})
    return render(request, 'public/contact.html')


# ---------------------------------------------------------------
# Auth views
# ---------------------------------------------------------------

def portal_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('staff_dashboard')
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password'],
        )
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('staff_dashboard')
            return redirect('dashboard')
        messages.error(request, _('Invalid username or password.'))
    return render(request, 'portal/login.html')


def portal_logout(request):
    logout(request)
    return redirect('home')


# ---------------------------------------------------------------
# Customer portal views
# ---------------------------------------------------------------

@login_required(login_url='login')
def dashboard(request):
    tickets = Ticket.objects.filter(
        customer=request.user.profile,
        status='open',
    ).order_by('-created_at')
    return render(request, 'portal/dashboard.html', {'tickets': tickets})


@login_required(login_url='login')
def ticket_archive(request):
    tickets = Ticket.objects.filter(
        customer=request.user.profile,
        status='closed',
    ).order_by('-updated_at')
    return render(request, 'portal/ticket_archive.html', {'tickets': tickets})


@login_required(login_url='login')
def ticket_new(request):
    if request.method == 'POST':
        ticket = Ticket.objects.create(
            customer=request.user.profile,
            title=request.POST['title'],
        )
        message = TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            body=request.POST['body'],
        )
        for img in request.FILES.getlist('images'):
            TicketImage.objects.create(message=message, image=img)
        messages.success(request, _('Your ticket has been submitted.'))
        return redirect('ticket_detail', ticket_id=ticket.id)
    return render(request, 'portal/ticket_new.html')


@login_required(login_url='login')
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(
        Ticket,
        id=ticket_id,
        customer=request.user.profile,
    )
    if request.method == 'POST' and ticket.status == 'open':
        message = TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            body=request.POST['body'],
        )
        for img in request.FILES.getlist('images'):
            TicketImage.objects.create(message=message, image=img)
        messages.success(request, _('Your reply has been sent.'))
        return redirect('ticket_detail', ticket_id=ticket.id)
    return render(request, 'portal/ticket_detail.html', {'ticket': ticket})


# ---------------------------------------------------------------
# Staff views
# ---------------------------------------------------------------

@staff_required
def staff_dashboard(request):
    tickets = Ticket.objects.filter(
        status='open'
    ).select_related('customer__user').order_by('-created_at')
    return render(request, 'staff/dashboard.html', {'tickets': tickets})


@staff_required
def staff_archive(request):
    tickets = Ticket.objects.filter(
        status='closed'
    ).select_related('customer__user').order_by('-updated_at')
    return render(request, 'staff/ticket_archive.html', {'tickets': tickets})


@staff_required
def staff_ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        if ticket.status == 'open':
            message = TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                body=request.POST['body'],
            )
            for img in request.FILES.getlist('images'):
                TicketImage.objects.create(message=message, image=img)
            messages.success(request, _('Reply sent.'))
        return redirect('staff_ticket_detail', ticket_id=ticket.id)
    return render(request, 'staff/ticket_detail.html', {'ticket': ticket})


@staff_required
def staff_close_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        ticket.status = Ticket.Status.CLOSED
        ticket.save()
        messages.success(request, _('Ticket closed.'))
    return redirect('staff_ticket_detail', ticket_id=ticket.id)


@staff_required
def staff_reopen_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        ticket.status = Ticket.Status.OPEN
        ticket.save()
        messages.success(request, _('Ticket reopened.'))
    return redirect('staff_ticket_detail', ticket_id=ticket.id)

@staff_required
def staff_leads(request):
    return render(request, 'staff/leads.html', {
        'new_leads':       Lead.objects.filter(is_contacted=False).order_by('-created_at'),
        'contacted_leads': Lead.objects.filter(is_contacted=True).order_by('-created_at'),
    })

@staff_required
def staff_toggle_lead(request, lead_id):
    if request.method == 'POST':
        lead = get_object_or_404(Lead, id=lead_id)
        lead.is_contacted = not lead.is_contacted
        lead.save()
    return redirect('staff_leads')


def staff_clients(request):
    clients = CustomerProfile.objects.select_related('user').order_by('-created_at')
    return render(request, 'staff/clients.html', {'clients': clients})

def staff_client_create(request):
    if request.method == 'POST':
        username     = request.POST.get('username')
        password     = request.POST.get('password')
        first_name   = request.POST.get('first_name')
        last_name    = request.POST.get('last_name')
        email        = request.POST.get('email')
        phone        = request.POST.get('phone', '')
        company_name = request.POST.get('company_name', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, _('Username "%(username)s" is already taken.') % {'username': username})
            return render(request, 'staff/client_create.html', {'form_data': request.POST})

        user = User.objects.create_user(
            username=username, password=password,
            first_name=first_name, last_name=last_name, email=email
        )
        CustomerProfile.objects.create(user=user, phone=phone, company_name=company_name)

        return render(request, 'staff/client_create.html', {
            'created_user': user,
            'created_password': password,  # shown once, then gone
        })

    return render(request, 'staff/client_create.html')



def staff_client_detail(request, pk):
    client = get_object_or_404(CustomerProfile, id=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            user = client.user
            user.first_name  = request.POST.get('first_name', '')
            user.last_name   = request.POST.get('last_name', '')
            user.email       = request.POST.get('email', '')
            user.username    = request.POST.get('username', user.username)
            new_pw = request.POST.get('new_password', '').strip()
            if new_pw:
                user.set_password(new_pw)
            user.save()
            client.phone        = request.POST.get('phone', '')
            client.company_name = request.POST.get('company_name', '')
            client.save()
            messages.success(request, _('Client updated successfully.'))
            return redirect('staff_client_detail', pk=pk)

        if action == 'delete':
            client.user.delete()  # cascades to CustomerProfile
            messages.success(request, _('Client account deleted.'))
            return redirect('staff_clients')

    return render(request, 'staff/client_detail.html', {'client': client})

def portal_change_password(request):
    if request.method == 'POST':
        new_pw  = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if new_pw != confirm:
            return render(request, 'portal/change_password.html', {'error_confirm': _('Passwords do not match.')})

        if len(new_pw) < 8:
            return render(request, 'portal/change_password.html', {'error_confirm': _('Password must be at least 8 characters.')})

        request.user.set_password(new_pw)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, _('Password updated successfully.'))
        return redirect('dashboard')

    return render(request, 'portal/change_password.html')