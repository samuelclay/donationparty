import datetime
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from donationparty.models import Round, Donation
from json_functions import json_encode
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
    round.expire_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    round.save()
    
    return HttpResponseRedirect(round.absolute_url())
    
def donation_create(request):
    round = get_object_or_404(Round, url=request.POST['round_id'])
    stripe_token = request.POST['stripeToken']
    name = request.POST['name']
    email = request.POST['email']
    amount = round.random_donation_amount()
    
    data = {
        'stripe_token': stripe_token,
        'amount': amount,
        'round': round,
        'name': name,
        'email': email,
    }
    donation = Donation.objects.create(**data)
    
    donation.charge_card()
    round.notify_subscribers()
    
    
    return round_status(request, round.url, donated=True)

def invite_emails(request):
    round = get_object_or_404(Round, url=request.POST['round_id'])
    invites = request.POST['invites']
    Emailer.email_invitees(round.absolute_url(), round.donations,
                               round.expire_time, invites)
    
def round_status(request, round_id, donated=False):
    round = get_object_or_404(Round, url=round_id)
    response = HttpResponse(mimetype='application/json')

    if donated:
        response.set_cookie(str('donated_%s' % round.url), 'yup')

    donations = round.donations.all()
    donations_template = render_to_string('donations.xhtml', {
        'donations': donations,
        'donated': True,
    })
    payment_info_template = render_to_string('payment_info.xhtml', {
        'round': round,
        'donated': True,
    })
    
    data = {
        'url': round.url,
        'charity': round.charity,
        'created': round.created,
        'closed': round.closed,
        'failed': round.failed,
        'seconds_left': round.seconds_left,
        'donations': [{
            'name': person.name,
            'created': person.created,
            'amount': round.closed and __builtins__['round'](person.amount, 2),
        } for person in donations],
        'donations_template': donations_template,
        'payment_info_template': payment_info_template,
    }
    
    response.write(json_encode(data))
    
    return response

def address_verification(request, round_id, secret_token):
    round = get_object_or_404(Round, url=round_id)
    if round.secret_token != secret_token:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        round.winner.name = request.POST['name']
        round.winning_address1 = request.POST['address1']
        round.winning_address2 = request.POST['address2']
        round.save()
        round.winner.save()
    
    return render_to_response('round_closed.xhtml', {
        'round': round,
        'settings': settings,
        'address_verification': True,
    }, context_instance=RequestContext(request))
    
def cron(request):
    Round.expire_rounds()