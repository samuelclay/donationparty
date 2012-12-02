from django.conf.urls import patterns, url, include

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'donationparty.views.home', name='home'),
    url(r'^round/(?P<round_id>\w+)/?', 'donationparty.views.round_page', name='round'),
    url(r'^round_status/(?P<round_id>\w+)/?', 'donationparty.views.round_status', name='round_status'),
    url(r'zebra/',   include('zebra.urls',  namespace="zebra",  app_name='zebra') ),
)
