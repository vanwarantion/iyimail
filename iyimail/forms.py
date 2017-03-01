from django.utils.translation import ugettext_lazy as _
from django import forms
from django.apps import apps

from .models import RuleTemplate


class RuleForm(forms.ModelForm):
    trigger_model = forms.ChoiceField(label="Trigger Model")
    class Meta:
        model = RuleTemplate
        exclude = []

    def __init__(self, *args, **kwargs):
        super(RuleForm, self).__init__(*args, **kwargs)
        model_choices = []
        for app_name in apps.all_models.keys():
            for i in apps.all_models[app_name]:
                model_choice_str = app_name + "." + i
                model_choices = model_choices + [(model_choice_str, model_choice_str),]
        self.fields['trigger_model'].choices = tuple(sorted(model_choices, key=lambda item: item[0]))
