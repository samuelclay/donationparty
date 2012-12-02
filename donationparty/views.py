from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from donationparty.models import Donation, Product, Charity, Round

def home(request):
    round = Round.objects.create(url=Round.generate_url())
    
    return HttpResponseRedirect(round.absolute_url())
    
def round_page(request, round_id):
    round = get_object_or_404(Round, url=round_id)
    
    if round.closed:
        return render_to_response('round_closed.xhtml', {
            'round': round,
        }, context_instance=RequestContext(request))
    elif round.charity:
        return render_to_response('round_running.xhtml', {
            'round': round,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('round_create.xhtml', {
            'round': round,
        }, context_instance=RequestContext(request))
        