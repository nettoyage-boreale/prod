from django.contrib import admin
from .models import CustomerProfile, Lead, Ticket, TicketMessage, TicketImage

admin.site.register(CustomerProfile)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display  = ('name', 'company', 'email', 'phone', 'service', 'created_at', 'is_contacted')
    list_filter   = ('service', 'is_contacted')
    search_fields = ('name', 'company', 'email')
    list_editable = ('is_contacted',)

admin.site.register(Ticket)
admin.site.register(TicketMessage)
admin.site.register(TicketImage)