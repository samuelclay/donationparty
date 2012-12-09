from django.db import models
from django.conf import settings
import hashlib
import uuid
import random
import stripe
import pusher
import datetime

class Round(models.Model):
    url = models.CharField(max_length=6, unique=True)
    charity = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey('Product', blank=True, null=True)
    expire_time = models.DateTimeField(blank=True, null=True)
    closed = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    max_amount = models.FloatField(default=10)
    
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
            "childsplay": "Childsplay",
            "redcross": "Red Cross",
            "oxfam": "Oxfam",
            "greenpeace": "Greenpeace",
        }
        return charities[self.charity]
        
    @classmethod
    def expire_rounds(cls):
        rounds = cls.objects.filter(closed=False,
                                    expire_time__lte=datetime.datetime.now())
        for round in rounds:
            round.expire_round()
    
    def expire_round(self):
        if self.closed or datetime.datetime.now() < self.expire_time:
            return
        
        self.closed = True
        donations = self.donations.all()
        total_raised = sum(donation.amount for donation in donations)
        if total_raised >= self.max_amount:
            self.failed = False
            # XXX TODO: Email everybody
        else:
            self.failed = True
            # XXX TODO: Email everybody
        self.save()
        
    def random_donation_amount(self):
        return max(1, random.random() * self.max_amount)
        
    def notify_subscribers(self):
        p = pusher.Pusher(app_id=settings.PUSHER_APP_ID,
                          key=settings.PUSHER_KEY,
                          secret=settings.PUSHER_SECRET)
        p[self.url].trigger('new:charge', {})
        
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
        return "https://www.gravatar.com/avatar/%s" % (
            hashlib.md5(self.email).hexdigest()
        )