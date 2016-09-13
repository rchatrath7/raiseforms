"""raiseforms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import forms.views as views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home),
    url(r'^home/$', views.home),
    url(r'^login/$', views.login_handler),
    url(r'^logout/$', views.logout_handler),
    url(r'^accounts/invite/$', views.invite_client),
    url(r'^accounts/register/(?P<auth_token>[\w\-]+)/$', views.register),
    url(r'^accounts/search/$', views.search),
    url(r'^clients/(?P<user_id>\d+)/$', views.client_panel),
    url(r'^clients/(?P<user_id>\d+)/contact/$', views.contact),
    url(r'^clients/(?P<user_id>\d+)/manage/$', views.manage),
    url(r'^clients/(?P<user_id>\d+)/manage/deactivate/$', views.deactivate),
    url(r'^clients/(?P<user_id>\d+)/manage/reactivate/$', views.reactivate),
    url(r'^clients/(?P<user_id>\d+)/forms/(?P<document_type>[\w\-]+)/$', views.onboard_forms),
    url(r'^clients/(?P<user_id>\d+)/forms/(?P<document_type>[\w\-]+)/remind_user/$', views.remind_user),
    url(r'^clients/(?P<user_id>\d+)/forms/(?P<document_type>[\w\-]+)/send/$', views.send_document),
    url(r'^clients/(?P<user_id>\d+)/forms/(?P<document_type>[\w\-]+)/retrieve/$', views.retrieve),
    url(r'^clients/(?P<user_id>\d+)/forms/(?P<document_type>[\w\-]+)/(?P<token>[\w\-]+)/$', views.tokenized_form_handler)
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
