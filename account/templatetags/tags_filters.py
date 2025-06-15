from django import template
from django.utils.safestring import mark_safe
from django import forms
from django.urls import reverse
from django.contrib.auth import get_user_model

register = template.Library()

@register.filter(name='form_as_p')
def form_as_p(form):
    output = []

    print(len(form.non_field_errors()))
    if form.non_field_errors():
            for error in form.non_field_errors():
                output.append('<p class="form-error">%s</p>' % (error))
    for field in form:
        if (not isinstance(field.field.widget, forms.CheckboxInput)):
            output.append('<p class="form-input-p">%s</p>' % (field.as_widget(attrs={'placeholder': field.label})))
        else:
             output.append('<p class="checkbox-input">%s%s</p>' % (field, field.label))

        if field.errors:
            for error in field.errors:
                output.append('<p class="error">%s</p>' % (error))

    return mark_safe(''.join(output))

@register.inclusion_tag(filename="account/update_link.html", takes_context=True)
def update_user_link(context):
    request = context['request']
    return {"is_social": get_user_model().social.filter(id=request.user.id).exists()}