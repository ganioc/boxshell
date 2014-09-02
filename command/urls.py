# Create your views here.
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$','command.views.main'),
    url(r'^get/$','command.views.get'),
    url(r'^set/$','command.views.set'),
    # url(r'^set_account/$','command.views.set_account'),
)
