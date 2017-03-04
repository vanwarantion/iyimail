# -*- coding: utf-8 -*-
__author__ = 'koray'

# https://github.com/vanwarantion/mtm/issues/135

from django.core.management.base import BaseCommand
from iyimail.models import RuleTemplate
from django.utils import timezone

class Command(BaseCommand):
    help = 'Send default user emails..'

    def add_arguments(self, parser):
        parser.add_argument(
            'rule_id',
            nargs='*',
            type=int,
            default=False
        )

    def handle(self, *args, **options):
        t = timezone.now()
        if options['rule_id']:
            rules_list = RuleTemplate.objects.filter(id__in=options['rule_id'])
            rules_list = rules_list.exclude(disable_at__lte=t).filter(activate_at__lte=t)
            self.stdout.write(self.style.HTTP_SUCCESS('Checking and sending %d rule templates...' % len(rules_list)))
        else:
            rules_list = RuleTemplate.objects.filter(activate_at__lte=t).exclude(disable_at__lte=t)
            self.stdout.write(self.style.HTTP_SUCCESS('No argument is given. Sending mails for all %d rule templates...' % len(rules_list)))
        total_sent = 0
        for i in rules_list:
            rule_mails = i.create_emails()
            for m in rule_mails:
                self.stdout.write(self.style.HTTP_SUCCESS('Sending %s to %s' % (i.template.name, m.recipient)))
                m.send()
                total_sent += 1
        self.stdout.write(self.style.SUCCESS('Sent %d emails' % (total_sent)))