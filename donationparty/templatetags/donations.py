from django import template

register = template.Library()

@register.inclusion_tag('donations.xhtml')
def render_donations(donations):
    return {'donations': donations}
    
@register.inclusion_tag('payment_info.xhtml', takes_context=True)
def render_payment_info(context, round, donated=False, **kwargs):
    if not donated:
        donated = context.get('request').COOKIES.get('donated_%s' % round.url)
    return {
        'context': context,
        'round': round,
        'donated': donated,
    }

@register.filter(name='round')
def round(value, arg):
    return __builtins__['round'](value, arg)