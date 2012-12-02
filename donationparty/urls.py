from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'donationparty.views.home', name='home'),
    url(r'^create$', 'donationparty.views.create', name='create'),
    url(r'^round$', 'donationparty.views.round', name='round'),
    url(r'^round_status$', 'donationparty.views.round_status', name='round_status'),
)
