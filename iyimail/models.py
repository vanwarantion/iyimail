from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template import Template, Context
import re

from django.db import models

class Email(models.Model):
    creation = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    recipient = models.EmailField(_("Recipient"))
    subject = models.CharField(_("Subject"), max_length=989, blank=True)
    message = models.TextField(_("Message"), blank=True)
    html_message = models.TextField(_("HTML Message"), blank=True)
    sent_at = models.DateTimeField(verbose_name=_("Sent At"), blank=True, null=True)

class EmailTemplate(models.Model):
    creation = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    subject = models.CharField(_("Subject"), max_length=989, default="")
    message = models.TextField(_("Message"), default="")
    html_message = models.TextField(_("HTML Message"), default="")

    def get_required_context(self):
        re_prog = re.compile('\{\{(.*?)\}\}')
        return [x.strip().split('.')[0] for x in re_prog.findall(self.subject + self.message + self.html_message)]

    def create_email(self, recipient, context = {}):
        for i in self.get_required_context():
            if i not in context.keys():
                raise AssertionError("Required context not found: %s" % i)
        my_context = Context(context)
        rv = Email(
            recipient=recipient,
            subject=Template(self.subject).render(my_context),
            message=Template(self.message).render(my_context),
            html_message=Template(self.html_message).render(my_context)
        )
        rv.save()
        return rv