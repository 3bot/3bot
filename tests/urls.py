"""URLs to run the tests."""
from django.conf.urls import include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^organizations/', include('organizations.urls')),
    url(r'^', include('threebot.urls')),
]
