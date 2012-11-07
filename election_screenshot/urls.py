from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'election_screenshot.views.home', name='home'),
    # url(r'^election_screenshot/', include('election_screenshot.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'screenshotter.views.state_index', name='index'),
    url(r'^status/$', 'screenshotter.views.status', name='status'),
    url(r'^states/$', 'screenshotter.views.state_index', name='state-index'),
    url(r'^state/(?P<state>[a-zA-Z]{2})/$', 'screenshotter.views.state_details', name='state-details'),
    url(r'^state/(?P<state>[a-zA-Z]{2})/(?P<sha1>[a-z0-9]{40})/$', 'screenshotter.views.url_details', name='url-details'),
)

