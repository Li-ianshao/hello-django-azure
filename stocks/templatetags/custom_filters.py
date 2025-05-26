from django import template

register = template.Library()

@register.filter
def percent_or_na(value):
    return f"{value}%" if isinstance(value, (int, float)) else value

@register.filter
def dollar_or_na(value):
    return f"${value}" if isinstance(value, (int, float)) else value
