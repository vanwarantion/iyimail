from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
import random
from .models import *
from .forms import RuleForm

class SentEmailFilter(admin.SimpleListFilter):
    title = _("Status")
    parameter_name = "sent"

    def lookups(self, request, model_admin):
        return (
            ('Yes', _("Sent")),
            ('No', _("Not Sent")),
        )

    def queryset(self, request, queryset):
        if self.value() == "Yes":
            return queryset.exclude(sent_at__isnull=True)
        if self.value() == "No":
            return queryset.filter(sent_at__isnull=True)

class EmailAdmin(admin.ModelAdmin):
    model = Email
    list_display = ['creation', 'recipient', 'sent_at', 'subject']
    search_fields = ['recipient', 'subject']
    list_filter = [SentEmailFilter]

admin.site.register(Email, EmailAdmin)

class TemplateAdmin(admin.ModelAdmin):
    model = EmailTemplate
    list_display = ['name', 'creation', 'subject']
    search_fields = ['subject', 'message', 'name']


admin.site.register(EmailTemplate, TemplateAdmin)

class RuleAdmin(admin.ModelAdmin):
    model = RuleTemplate
    form = RuleForm
    list_display = ['template', 'trigger_model']
    preview_context = None
    list_filter = (
        ('template', admin.RelatedOnlyFieldListFilter),
    )

    def triggered_object_count(self, obj):
        return len(obj.get_triggered_objects())
    triggered_object_count.allow_tags = True
    triggered_object_count.short_description = "Currently Triggered Objects"

    def example_context(self, obj):
        random_obj = random.choice(list(obj.get_triggered_objects()))
        context_method = getattr(random_obj, obj.context_method_name, None)
        self.preview_context = context_method()
        if context_method:
            return "%s: %s" %(random_obj, str(self.preview_context)[:500])
    example_context.allow_tags = True
    example_context.short_description = "Example Context Output"

    def preview(self, obj):
        obj_url = obj.get_absolute_url()
        return '<iframe src="%s"></iframe><p class="help"><a href="%s" target="_blank">%s</a><p>' % (
            obj_url, obj_url, _("View in browser")
        )
    preview.allow_tags = True
    preview.short_description = "Example Email"

    def get_readonly_fields(self, request, obj=None):
        rf = []
        if hasattr(obj, 'pk'):
            rf.append('triggered_object_count')
            if self.triggered_object_count(obj) > 0:
                rf.append('example_context')
                rf.append('preview')
        return rf

admin.site.register(RuleTemplate, RuleAdmin)