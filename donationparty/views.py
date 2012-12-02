from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from donationparty.models import Round, Donation
import json
from email import Emailer

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
    
    round.charity = charity_name
    round.save()
    
    return HttpResponseRedirect(round.absolute_url())
    
def donation_create(request):
    round = get_object_or_404(Round, url=request.POST['round_id'])
    stripe_token = request.POST['stripeToken']
    amount = round.donation_amount()
    
    data = {
        'stripe_token': stripe_token,
        'amount': amount,
        'round': round,
    }
    donation = Donation.objects.create(**data)
    
    donation.charge()
    round.notify_subscribers()
    
    return HttpResponseRedirect(round.absolute_url())

def invite_emails(request):
    round = get_object_or_404(Round, url=request.POST['round_id'])
    invites = get_object_or_404(Round, url=request.POST['invites'])
    Emailer.email_invitees(round.absolute_url(), round.donations,
                               round.expire_time, invites)
    
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
