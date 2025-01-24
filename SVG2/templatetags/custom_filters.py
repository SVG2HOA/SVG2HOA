from django import template

register = template.Library()

@register.filter
def get_initial_value(vehicle, form):
    # Assuming 'form' contains the vehicle data
    field_name = f"vehicle_{vehicle}"
    if field_name in form.fields:
        return form.fields[field_name].initial
    return 0  # Return a default value if not found
