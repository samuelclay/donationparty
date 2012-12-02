from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from donationparty.models import Round, Donation
import json

def home(request):
    round = Round.objects.create(url=Round.generate_url())
    
    return HttpResponseRedirect(round.absolute_url())
    
def round_page(request, round_id):
    round = get_object_or_404(Round, url=round_id)

    if request.method == "POST":
        return round_create(request, round_id)
    
    if round.closed:
        return render_to_response('round_closed.xhtml', {
            'round': round,
            'settings': settings,
        }, context_instance=RequestContext(request))
    elif round.charity:
        return render_to_response('round_running.xhtml', {
            'round': round,
            'settings': settings,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('round_create.xhtml', {
            'round': round,
            'settings': settings,
        }, context_instance=RequestContext(request))

def round_create(request, round_id):
    round = get_object_or_404(Round, url=round_id)
    charity_name = request.POST['charity']
    invitees = request.POST['invitees']
    
    round.charity = charity_name
    round.invitees = invitees
    round.save()
    
    # XXX TODO: Parse invitees and send email
    return render_to_response('round_running.xhtml', {
        'round': round,
        'settings': settings,
    }, context_instance=RequestContext(request))

def donation_create(request):
    round = get_object_or_404(Round, request.POST['round_id'])
    name = request.POST['name']
    email = request.POST['email']
    stripe_token = request.POST['stripe_token']
    amount = round.donation_amount()
    
    data = {
        'name': name,
        'email': email,
        'stripe_token': stripe_token,
        'amount': amount,
        'round': round,
    }
    donation = Donation.objects.create(**data)
    
    donation.charge()
    round.notify_subscribers()
    
    return HttpResponse(json.encode({'message': 'OK', 'code': 1}), 
                        mimetype='application/json')
    
def round_status(request, round_id):
    round = get_object_or_404(Round, url=round_id)
    people = round.donations.all()
    
    data = {
        'url': round.url,
        'charity': round.charity,
        'created': round.created,
        'closed': round.closed,
        'failed': round.failed,
        'people': [{
            'name': person.name,
            'created': person.created,
            'amount': round.closed and person.amount,
        } for person in people],
    }
    return HttpResponse(json.encode(data), mimetype='application/json')