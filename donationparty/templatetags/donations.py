from django import template

register = template.Library()

@register.inclusion_tag('donations.xhtml')
def render_donations(donations):
    return {'donations': donations}
    
@register.filter(name='round')
def round(value, arg):
    return __builtins__['round'](value, arg)