from django.conf.urls import patterns, url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'donationparty.views.home', name='home'),
    url(r'^round/(?P<round_id>\w+)/?', 'donationparty.views.round_page', name='round'),
    url(r'^round_status/(?P<round_id>\w+)/?', 'donationparty.views.round_status', name='round_status'),
    url(r'^address/(?P<round_id>\w+)/(?P<secret_token>\w+)/?', 'donationparty.views.address_verification', name='address_verification'),
    url(r'^charge/?', 'donationparty.views.donation_create', name='donation_create'),
    url(r'^invite/?', 'donationparty.views.invite_emails', name='invite_emails'),
)

urlpatterns += staticfiles_urlpatterns()