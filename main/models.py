from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()}  {self.company_name}"


class Lead(models.Model):
    class Service(models.TextChoices):
        OFFICE    = 'office',    'Office Cleaning'
        CLINIC    = 'clinic',    'Clinic / Medical'
        WAREHOUSE = 'warehouse', 'Warehouse / Industrial'
        RETAIL    = 'retail',    'Retail / Commercial'
        OTHER     = 'other',     'Other'

    name         = models.CharField(max_length=100)
    company      = models.CharField(max_length=150, blank=True)
    email        = models.EmailField()
    phone        = models.CharField(max_length=20, blank=True)
    service      = models.CharField(max_length=20, choices=Service.choices, blank=True)
    message      = models.TextField()
    created_at   = models.DateTimeField(auto_now_add=True)
    is_contacted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}  {self.email}"


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.status.upper()}] {self.title}"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.username} on ticket #{self.ticket.id}"


class TicketImage(models.Model):
    message = models.ForeignKey(TicketMessage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tickets/', storage=MediaCloudinaryStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)

    