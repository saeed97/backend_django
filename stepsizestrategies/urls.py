#!/home/stepsizestrategies/.local/bin/python3



from django.conf.urls import url,include


import strategies.views



# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', admin.site.urls),

       url(r'^$', strategies.views.index, name='index'),

       url(r'^login/$', strategies.views.login_view, name="login"),

    url(r'^register/$', strategies.views.register_view, name="register_view"),

    url(r'^logout/$', strategies.views.logout_view, name="logout"),

     url(r'^contact/$', strategies.views.about, name="contact"),
     url(r'^find/$', strategies.views.find, name="explore"),
     url(r'^listing/$', strategies.views.listing, name="listing"),
     url(r'^profile/$', strategies.views.profile, name="profile"),






]