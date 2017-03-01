from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import random
from .models import RuleTemplate

def preview(request, ruleID):
    my_rule = get_object_or_404(RuleTemplate, pk=ruleID)
    random_obj = random.choice(list(my_rule.get_triggered_objects()))
    context_method = getattr(random_obj, my_rule.context_method_name, None)
    preview_context = context_method()
    rendered_content = my_rule.template.render_text(my_rule.template.html_message, preview_context)
    return HttpResponse(rendered_content)