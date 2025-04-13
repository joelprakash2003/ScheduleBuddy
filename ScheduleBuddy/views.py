# views.py (update with updated create_meeting view)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Ministry, Assignment, Meeting
from .forms import LoginForm
import json

User = get_user_model()


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember') == 'on'
        # Authenticate + login logic here
    return render(request, 'login.html')


def user_organizations_view(request):
    return render(request, 'user-organizations.html')

def main_org_view(request):
    return render(request, 'main-org.html')

def org_services_view(request):
    return render(request, 'org-services.html')

def org_teams_view(request):
    return render(request, 'org-teams.html')

def org_people_view(request):
    return render(request, 'org-people.html')

def org_messages_view(request):
    return render(request, 'org-messages.html')