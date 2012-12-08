from django.db import models
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.utils import simplejson as json
from decimal import Decimal
import datetime

def json_encode(data, *args, **kwargs):
    """
    The main issues with django's default json serializer is that properties that
    had been added to an object dynamically are being ignored (and it also has 
    problems with some models).
    """

    def _any(data):
        ret = None
        # Opps, we used to check if it is of type list, but that fails 
        # i.e. in the case of django.newforms.utils.ErrorList, which extends
        # the type "list". Oh man, that was a dumb mistake!
        if hasattr(data, 'to_json'):
            ret = _any(data.to_json())
        elif hasattr(data, 'canonical'):
            ret = data.canonical()
        elif isinstance(data, list):
            ret = _list(data)
        elif isinstance(data, set):
            ret = _list(list(data))
        # Same as for lists above.
        elif isinstance(data, dict):
            ret = _dict(data)
        elif isinstance(data, models.query.QuerySet):
            # Actually its the same as a list ...
            ret = _list(data)
        elif isinstance(data, models.Model):
            ret = _model(data)
        # here we need to encode the string as unicode (otherwise we get utf-16 in the json-response)
        elif isinstance(data, basestring):
            ret = unicode(data)
        # see http://code.djangoproject.com/ticket/5868
        elif isinstance(data, Promise):
            ret = force_unicode(data)
        elif isinstance(data, datetime.datetime) or isinstance(data, datetime.date):
            ret = str(data)
        else:
            ret = data
        return ret
    
    def _model(data):
        ret = {}
        # If we only have a model, we only want to encode the fields.
        for f in data._meta.fields:
            ret[f.attname] = _any(getattr(data, f.attname))
        # And additionally encode arbitrary properties that had been added.
        fields = dir(data.__class__) + ret.keys()
        add_ons = [k for k in dir(data) if k not in fields]
        for k in add_ons:
            ret[k] = _any(getattr(data, k))
        return ret
    
    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret
    
    def _dict(data):
        ret = {}
        for k,v in data.items():
            ret[str(k)] = _any(v)
        return ret
    
    if hasattr(data, 'to_json'):
        data = data.to_json()
    ret = _any(data)
    return json.dumps(ret)
