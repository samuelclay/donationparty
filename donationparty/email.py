from datetime import datetime
from django.conf import settings
from django.core.mail import send_mass_mail


class Emailer:
  @staticmethod
  def email_invitees(round_url, round_creator, round_expiration, round_invitees):
    invitees_list = round_invitees.split(',')
    subject = "%s has invited you to a Donation Party!" %(round_creator)
    time_left = round_expiration - datetime.now

    #TODO: Fancy email
    email_body = """
    %s has invited you to a Donation Party! 
    You have %d hours %d minutes left to <a href='https://%s%s'>donate!</a>
    """ %(round_creator, time_left.hours, time_left.minutes, settings.SSL_HOST, round_url)
    send_mass_mail(subject, email_body, 'invite@donationparty.com',
              invitees_list, fail_silently=False)