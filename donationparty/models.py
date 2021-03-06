from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
import hashlib
import uuid
import random
import stripe
import pusher
import datetime

from email import Emailer

class Round(models.Model):
    url = models.CharField(max_length=6, unique=True)
    charity = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey('Product', blank=True, null=True)
    expire_time = models.DateTimeField(blank=True, null=True)
    closed = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    max_amount = models.FloatField(default=10)
    winning_address1 = models.CharField(max_length=255, blank=True, null=True)
    winning_address2 = models.CharField(max_length=255, blank=True, null=True)
    secret_token = models.CharField(max_length=40, blank=True, null=True)
    
    def absolute_url(self):
        return '/round/%s' % self.url
    
    @classmethod
    def generate_url(cls):
        # XXX TODO: check for collision
        url = unicode(uuid.uuid4())[:6]
        return url
    
    @property
    def charity_name(self):
        charities = {
            "eff": "Electronic Frontier Foundation",
            "childsplay": "Child's Play",
            "redcross": "American Red Cross",
            "oxfam": "Oxfam",
            "greenpeace": "Greenpeace",
        }
        return charities[self.charity]
    
    @property
    def seconds_left(self):
        return (self.expire_time - datetime.datetime.now()).seconds
        
    @classmethod
    def expire_rounds(cls):
        rounds = cls.objects.filter(closed=False,
                                    expire_time__lte=datetime.datetime.now())
        for round in rounds:
            round.expire_round()
    
    def expire_round(self, force=False):
        if not force and (self.closed or datetime.datetime.now() < self.expire_time):
            return
        
        self.closed = True
        if self.total_raised() >= self.max_amount*2 or self.donations.count() >= 3:
            self.failed = False
            self.secret_token = str(uuid.uuid4())[:40].replace('-', '')
        else:
            self.failed = True
        self.save()

        Emailer.round_over(self)
        
    def random_donation_amount(self):
        return max(1, random.random() * self.max_amount)
        
    def notify_subscribers(self):
        p = pusher.Pusher(app_id=settings.PUSHER_APP_ID,
                          key=settings.PUSHER_KEY,
                          secret=settings.PUSHER_SECRET)
        p[self.url].trigger('new:charge', {})
    
    def address_verification_url(self):
        return reverse('address_verification', kwargs=dict(round_id=self.url, secret_token=self.secret_token))

    def total_raised(self):
        return sum(donation.amount for donation in self.donations.all())
        
    @property
    def winner(self):
        donations = self.donations.all()
        max_donator = None
        for donation in donations:
            if not max_donator or donation.amount > max_donator.amount:
                max_donator = donation
        
        return max_donator
        
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    amazon_id = models.TextField()
    

class Donation(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=255)
    round = models.ForeignKey(Round, related_name='donations')
    created = models.DateTimeField(auto_now=True)
    stripe_token = models.CharField(max_length=255)
    amount = models.FloatField()
    
    def charge_card(self):
        amount = int(self.amount * 100)
        try:
            stripe.Charge.create(card=self.stripe_token,
                                 amount=amount,
                                 currency='usd')
        except stripe.InvalidRequestError, e:
            print "STRIPE ERRROR: %s" % e
    
    def gravatar_url(self):
        return "https://www.gravatar.com/avatar/%s?d=retro" % (
            hashlib.md5(self.email).hexdigest()
        )
