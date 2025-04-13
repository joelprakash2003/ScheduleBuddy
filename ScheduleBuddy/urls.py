# ScheduleBuddy/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import *

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='home'),
    path('user-organizations/', user_organizations_view, name='user_organizations'),
    path('main-org/', main_org_view, name='main_org'),
    path('org-services/', org_services_view, name='org_services'),
    path('org-teams/', org_teams_view, name='org_teams'),
    path('org-people/', org_people_view, name='org_people'),
    path('org-messages/', org_messages_view, name='org_messages'),
]
