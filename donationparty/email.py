from datetime import datetime
from django.conf import settings
from django.core import mail

from templated_email import get_templated_mail

def multi_templated_email(templateName, to_emails, from_email, context):
    """
    send separate emails to multiple recipients using a template
    """
    for to in to_emails:
      email = get_templated_mail(templateName, context=context, from_email=from_email, to=[to])
      email.send()

class Emailer:
  @staticmethod
  def email_invitees(round_url, round_donations, round_expiration, round_invitees):
    """
    email sent by round creator to invite other people to the round by email
    """
    email_from = 'invite@donationparty.com'
    invitees_list = round_invitees.split(',')
    time_left = round_expiration.replace(tzinfo=None) - datetime.now().replace(tzinfo=None)
    round_donation_str = "Fake Person, Another Fake Person" #TODO: r.name for r in round_donations
    
    for invitee in invitees_list:
        email = get_templated_mail('invite', context={}, from_email=email_from, to=[invitee])
        email.send()
