# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Ministry, Assignment, Meeting
from .forms import LoginForm
import json
import requests
from .forms import EmailForm, OTPForm, NewUserForm

User = get_user_model()

API_BASE = "https://api.worshipbuddy.org"
STAGING_BASE = "https://api.worshipbuddy.org"

def login_view(request):
    message = ""
    step = "email"

    if request.method == "POST":
        if "otp" in request.POST:
            form = OTPForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                otp = form.cleaned_data['otp']
                res = requests.post(f"{API_BASE}/auth/verify-otp/", json={
                    "email": email,
                    "otp": otp
                })
                data = res.json()
                if res.ok:
                    if data.get("is_new_user"):
                        step = "new_user"
                        form = NewUserForm(initial={"email": email})
                    else:
                        request.session["user_email"] = email
                        return redirect("/user-organizations/")
                else:
                    message = data.get("detail", "OTP verification failed.")
        elif "first_name" in request.POST:
            form = NewUserForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                payload = {
                    "first_name": form.cleaned_data["first_name"],
                    "last_name": form.cleaned_data["last_name"],
                    "church": form.cleaned_data["church"],
                    "schedulebuddy": { "organizations": [] }
                }
                res = requests.put(f"{API_BASE}/users/{email}", json=payload)
                if res.ok:
                    request.session["user_email"] = email
                    return redirect("/user-organizations/")
                else:
                    message = res.json().get("detail", "Profile update failed.")
        else:
            form = EmailForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                res = requests.post(f"{API_BASE}/auth/request-otp/", json={ "email": email })
                data = res.json()
                if res.ok:
                    step = "otp"
                    form = OTPForm(initial={ "email": email })
                    message = data.get("message", "OTP sent to your email.")
                else:
                    message = data.get("detail", "Failed to send OTP.")
    else:
        form = EmailForm()

    return render(request, "registration/login.html", {
        "form": form,
        "step": step,
        "message": message
    })


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