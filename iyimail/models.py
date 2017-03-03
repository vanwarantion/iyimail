from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.template import Template, Context
from django.core.urlresolvers import reverse
from django.apps import apps
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError, FieldError
from datetime import datetime, timedelta
import re, inspect, pytz

from django.db import models

FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", "admin@example.com")

class Email(models.Model):
    creation = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    recipient = models.EmailField(_("Recipient"))
    subject = models.CharField(_("Subject"), max_length=989, blank=True)
    message = models.TextField(_("Message"), blank=True)
    html_message = models.TextField(_("HTML Message"), blank=True)
    sent_at = models.DateTimeField(verbose_name=_("Sent At"), blank=True, null=True)

    def get_recipients(self):
        return [self.recipient]

    def send(self):
        send_mail(
            subject=self.subject,
            message=self.message,
            from_email=FROM_EMAIL,
            recipient_list=self.get_recipients(),
            html_message=self.html_message)
        self.sent_at = datetime.utcnow()
        self.save()

class EmailTemplate(models.Model):
    name = models.CharField(_("Name"), max_length=120, help_text=_("Designated handle"), unique=True)
    creation = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    subject = models.CharField(_("Subject"), max_length=989, default="",
                               help_text=_("Hint: You can use Django's template tags"))
    message = models.TextField(_("Message"), default="", help_text=_("Hint: You can use Django's template tags"))
    html_message = models.TextField(_("HTML Message"), default="",
                                    help_text=_("Hint: You can use Django's template tags"))

    class Meta:
        verbose_name = "Template"

    def get_required_context(self):
        re_prog = re.compile('\{\{(.*?)\}\}')
        return [x.strip().split('.')[0] for x in re_prog.findall(self.subject + self.message + self.html_message)]

    def __str__(self):
        return self.name

    def render_text(self, txt_2_render, context):
        return Template(txt_2_render).render(Context(context))

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

def validate_trigger_age(val):
    timedelta_members = inspect.getmembers(timedelta, lambda a:not(inspect.isroutine(a)))
    members_list = filter(lambda n: n[0] != '_', [x[0] for x in timedelta_members])
    test_args = {}
    for i in val.split(','):
        td_arg, td_val = i.split('=')

        try:
            td_val = int(td_val)
        except ValueError:
            raise ValidationError(_("%(a)s needs to be an integer"), params={'a': td_arg})

        if td_val <= 0:
            raise ValidationError(_("%(a)s needs to be a positive integer"), params={'a': td_arg})

        if isinstance(td_val, int) == False:
            raise ValidationError(_("%(a)s is not a valid parameter"), params={'a': td_val})

        if isinstance(td_arg, unicode) == False:
            raise ValidationError(_("%(a)s (%(at)s) is not a valid argument"), params={'a': td_arg, 'at': type(td_arg)})

        if td_arg.strip() not in members_list:
            raise ValidationError(_("%(a)s is not a valid argument for timedelta()"), params={'a': td_arg})

        test_args[td_arg] = td_val

    try:
        td = timedelta(**test_args)
    except TypeError:
        raise ValidationError(_("%(a)s does not contain valid parameters for timedelta"), params={'a': val})

    if isinstance(td, timedelta) == False:
        raise ValidationError(_("%(a)s does not return a valid timedelta object"), params={'a': val})

class RuleTemplate(models.Model):
    template = models.ForeignKey('EmailTemplate', verbose_name=_("Email Template"))
    trigger_model = models.CharField(max_length=500, verbose_name=_("Trigger Model"))
    trigger_query_str = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Model Argument"),
                                         help_text=_("Filter Argument"))
    trigger_age = models.CharField(max_length=100, null=True, blank=True, validators=[validate_trigger_age],
                                   verbose_name=_("Trigger Age"),
                                   help_text=_('Timedelta based triggers only. Eg. Enter "days=3" for timedelta(days=3)'))
    trigger_condition = models.CharField(max_length=500, null=True, blank=True, help_text=_("Overrides Trigger Age"),
                                         verbose_name=_("Trigger Condition"))
    context_method_name = models.CharField(max_length=500, verbose_name=_("Context Method Name"),
                                           help_text=_("Method name that returns context required by Email Template"))
    email_address_field = models.CharField(max_length=500, default='email', verbose_name=_("Email Address Field"),
                                           help_text=_("Field name that returns Email address of the recipient."))


    class Meta:
        verbose_name = "Rule"

    def clean(self):
        # Check if context_method_name is callable
        source_model = self.get_source_model()
        trigger_method = getattr(source_model, self.context_method_name, None)
        if callable(trigger_method) == False:
            raise ValidationError(_("%(a)s is not a valid method name for context"), params={'a': self.context_method_name})
        # Check trigger_age
        source_model = self.get_source_model()
        td_kwargs = self.get_age_parameters()
        if td_kwargs:
            filter_q = {
                self.trigger_query_str: datetime.now(tz=pytz.timezone('Australia/Brisbane')) - timedelta(**td_kwargs)
            }
            try:
                test_qs = source_model.objects.filter(**filter_q)
            except FieldError:
                raise ValidationError(_("%(a)s is invalid"), params={'a': self.trigger_query_str})
        else:
            test_qs = source_model.objects.all()
        # Check if required context is returned
        if len(test_qs) > 0:
            context_method = getattr(test_qs[0], self.context_method_name, None)
            if callable(context_method):
                mail_context = context_method()
                req_context = self.template.get_required_context()
                for i in req_context:
                    if i not in mail_context:
                        raise ValidationError(
                            _("%(a)s does not contain required context: %(c)s"),
                            params={'a': self.trigger_query_str, 'c': str(req_context)}
                        )

    def __str__(self):
        return u"%d: %s" % (self.id, self.template.name)

    def get_absolute_url(self):
        return reverse('rule-preview', args=[str(self.id)])

    def get_source_model(self):
        app_name, model_name = self.trigger_model.split(".")
        return apps.get_model(app_name, model_name)

    def get_age_parameters(self):
        if self.trigger_condition:
            return None
        if self.trigger_age:
            td_kwargs = {}
            for i in self.trigger_age.split(','):
                td_arg, td_val = i.split('=')
                td_kwargs[td_arg.strip()] = int(td_val)
            return td_kwargs

    def get_triggered_objects(self):
        source_model = self.get_source_model()
        if self.trigger_condition:
            filter_q = {self.trigger_query_str:self.trigger_condition}
            return source_model.objects.filter(**filter_q)
        if self.trigger_age:
            td_kwargs = self.get_age_parameters()
            filter_q = {
                self.trigger_query_str: datetime.now(tz=pytz.timezone('Australia/Brisbane')) - timedelta(**td_kwargs)
            }
            try:
                return source_model.objects.filter(**filter_q)
            except FieldError:
                print ""
        return source_model.objects.all()

    def make_log(self, recipient):
        ExecutionLog(self, recipient)
        ExecutionLog.save()

    def create_emails(self):
        field_path = self.email_address_field.split('.')

        def get_email(obj):
            attr = obj
            for i in field_path:
                try:
                    attr = getattr(attr, i)
                except AttributeError:
                    return None
            return attr

        rv = []
        ex_mails_list = self.executionlog_set.values_list('email', flat=True)
        for i in self.get_triggered_objects():
            rcpt_address = get_email(i)
            if rcpt_address in ex_mails_list:
                # Skip if recipient in execution log
                continue
            context_method = getattr(i, self.context_method_name, None)
            if callable(context_method):
                mail_context = context_method()
                rv.append(self.template.create_email(rcpt_address, mail_context))

        return rv

class ExecutionLog(models.Model):
    creation = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    rule = models.ForeignKey('RuleTemplate')
    email = models.OneToOneField('Email')
