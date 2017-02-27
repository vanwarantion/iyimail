from django.contrib import admin
from .models import *

class EmailAdmin(admin.ModelAdmin):
    model = Email
    list_display = ['creation', 'recipient', 'sent_at', 'subject']
    search_fields = ['recipient', 'subject']

admin.site.register(Email, EmailAdmin)

class TemplateAdmin(admin.ModelAdmin):
    model = EmailTemplate
    list_display = ['creation', 'subject']
    search_fields = ['subject', 'message']

admin.site.register(EmailTemplate, TemplateAdmin)