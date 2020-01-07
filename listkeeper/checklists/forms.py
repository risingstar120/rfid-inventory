import hashlib

from django import forms

from .models import Template, Run


class RunForm(forms.ModelForm):
    """
    Custom run edit form that includes dynamic options for the questions.
    """

    class Meta:
        model = Run
        fields = ["name", "template"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make a field per condition
        if self.instance.id:
            for condition in self.instance.template.conditions:
                current_conditions = self.instance.conditions or []
                self.fields[self.condition_field_name(condition)] = forms.BooleanField(
                    label=condition,
                    required=False,
                    initial=condition in current_conditions,
                )

    def save(self, *args, **kwargs):
        kwargs["commit"] = False
        instance = super().save(*args, **kwargs)
        instance.conditions = []
        for condition in instance.template.conditions:
            if self.cleaned_data.get(self.condition_field_name(condition), False):
                instance.conditions.append(condition)
        instance.save()
        return instance

    def condition_field_name(self, condition):
        hash_value = hashlib.md5(condition.encode("utf8")).hexdigest()
        return "condition_%s" % hash_value
