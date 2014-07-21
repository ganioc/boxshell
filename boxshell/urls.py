
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'boxshell.views.home', name='home'),
    # url(r'^boxshell/', include('boxshell.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$','boxshell.views.home'),
    url(r'^switch_language/$','boxshell.views.switch_language'),
    url(r'^about/$','boxshell.views.about'),
    url(r'^contact/$','boxshell.views.contact'),
    url(r'^signin/$','boxshell.views.signin'),
    url(r'^register/$','boxshell.views.register'),
    url(r'^activate/$','boxshell.views.activate'),
    url(r'^terms/$','boxshell.views.terms'),    
    url(r'^command/', include('command.urls')),
    url(r'^account/', 'boxshell.views.account'),
    url(r'^signout/', 'boxshell.views.signout'),
   # url(r'^smith/',include('smith.urls')),
    # url(r'^teapot/',include('teapot.urls')),    
)
