from django import template
import datetime
from django.utils.translation import ungettext

register = template.Library()

@register.inclusion_tag('donations.xhtml', takes_context=True)
def render_donations(context, round):
    donated = context.get('request').COOKIES.get('donated_%s' % round.url)
    return {
        'donated': donated,
        'donations': round.donations.all,
    }
    
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
    
@register.filter(name='relative')
def relative(value):
    if not value:
        return u''
    
    chunks = (
      (60 * 60 * 24 * 30, lambda n: ungettext('month', 'months', n)),
      (60 * 60 * 24, lambda n: ungettext('day', 'days', n)),
      (60 * 60, lambda n: ungettext('hour', 'hours', n)),
      (60, lambda n: ungettext('minute', 'minutes', n)),
      (1, lambda n: ungettext('second', 'seconds', n)),
      (0, lambda n: 'just now'),
    )
    return _do_timesince(value, chunks)
    
def _do_timesince(d, chunks, now=None):
    """
    Started as a copy of django.util.timesince.timesince, but modified to
    only output one time unit, and use months as the maximum unit of measure.
    
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
    then "0 minutes" is returned.

    Units used are months, weeks, days, hours, and minutes.
    Seconds and microseconds are ignored.
    """
    # Convert datetime.date to datetime.datetime for comparison
    if d.__class__ is not datetime.datetime:
        d = datetime.datetime(d.year, d.month, d.day)

    if not now:
        now = datetime.datetime.utcnow()

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond)).replace(tzinfo=None)
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since > 10:
        for i, (seconds, name) in enumerate(chunks):
            count = since // seconds
            if count != 0:
                break
        s = '%(number)d %(type)s' % {'number': count, 'type': name(count)}
    else:
        s = 'just a second'
    return s
