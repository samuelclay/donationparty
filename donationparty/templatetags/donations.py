from django import template

register = template.Library()

@register.inclusion_tag('donations.xhtml')
def render_donations(donations):
    return {'donations': donations}