from django.conf import settings
from django.http import HttpResponseRedirect, get_host

SSL = 'SSL'

class SSLRedirect:
    
    def process_request(self, request):
        if not request.is_secure():
            return self._redirect(request)

    def _redirect(self, request):
        host = getattr(settings, 'SSL_HOST', get_host(request))
        newurl = "https://%s%s" % (host,request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
        """Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs."""

        return HttpResponseRedirect(newurl)