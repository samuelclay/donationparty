from django.db import models
import uuid
import random
import stripe
from email import Emailer
import pusher

class Round(models.Model):
    url = models.CharField(max_length=6, unique=True)
    charity = models.CharField(max_length=255, blank=True, null=True)
    invites = models.TextField(blank=True, null=True)
    product = models.ForeignKey('Product', blank=True, null=True)
    expire_time = models.DateTimeField(blank=True, null=True)
    closed = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    max_amount = models.FloatField(blank=True, null=True)
    
    def absolute_url(self):
        return '/round/%s' % self.url
    
    @classmethod
    def generate_url(cls):
        # XXX TODO: check for collision
        url = unicode(uuid.uuid4())[:6]
        return url

    def donate_amount(self):
        return random.random() * self.max_amount
        
    def notify_subscribers(self):
        p = pusher.Pusher()
        p[self.url].trigger('new_donation', {})
        
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

    def charge(self):
        stripe.charge(customer=self.stripe_token, amount=self.amount)

    def send_invites_if_first(self):
        """ When the first donation is added to a round email the invitees"""
        if self.round.donations.count == 1:
            Emailer.email_invitees(self.round.absolute_url(), self.name, 
                                   self.round.expire_time, self.round.invites)