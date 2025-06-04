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
from django.conf import settings

User = get_user_model()

API_BASE = "https://api.worshipbuddy.org"


def login_view(request):
    message = ""
    message_class = ""
    stage = request.POST.get("stage", "request_otp")  # default stage
    email = request.POST.get("email", "").strip()
    otp = request.POST.get("otp", "").strip()
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    church = request.POST.get("church", "").strip()

    ctx = {
        "email": email,
        "show_otp_group": False,
        "readonly_email": False,
        "show_email_controls": False,
        "show_new_user_fields": False,
        "button_text": "Request One-Time Password",
        "message": message,
        "message_class": message_class,
    }

    if request.method == "POST":
        if stage == "request_otp":
            if not email:
                ctx.update({
                    "message": "Please enter your email.",
                    "message_class": "error",
                })
            else:
                resp = requests.post(f"{API_BASE}/auth/request-otp/", json={"email": email})
                data = resp.json()
                if not resp.ok:
                    ctx.update({
                        "message": data.get("detail", "OTP request failed"),
                        "message_class": "error",
                    })
                else:
                    ctx.update({
                        "show_otp_group": True,
                        "readonly_email": True,
                        "show_email_controls": True,
                        "button_text": "Verify One-Time Password",
                        "message": data.get("message", ""),
                        "message_class": "success",
                    })
                    stage = "verify_otp"

        elif stage == "verify_otp":
            if not otp:
                ctx.update({
                    "email": email,
                    "show_otp_group": True,
                    "readonly_email": True,
                    "show_email_controls": True,
                    "button_text": "Verify One-Time Password",
                    "message": "Please enter the OTP.",
                    "message_class": "error",
                })
            else:
                resp = requests.post(f"{API_BASE}/auth/verify-otp/", json={"email": email, "otp": otp})
                data = resp.json()
                if not resp.ok:
                    ctx.update({
                        "email": email,
                        "show_otp_group": True,
                        "readonly_email": True,
                        "show_email_controls": True,
                        "button_text": "Verify One-Time Password",
                        "message": data.get("detail", "OTP verification failed"),
                        "message_class": "error",
                    })
                else:
                    is_new = data.get("is_new_user", False)
                    if is_new:
                        ctx.update({
                            "show_new_user_fields": True,
                            "message": data.get("message", ""),
                            "message_class": "success",
                            "show_otp_group": False,
                            "show_email_controls": False,
                            "button_text": "Complete Account",
                            "email": email,
                            "readonly_email": True,
                        })
                        stage = "complete_profile"
                    else:
                        user = data.get("user", {})
                        if not user.get("schedulebuddy") or not user["schedulebuddy"].get("organizations"):
                            requests.put(
                                f"{API_BASE}/users/{email}",
                                json={"schedulebuddy": {"organizations": []}},
                            )
                        user_info = {}
                        try:
                            r = requests.get(f"{API_BASE}/users/{email}")
                            user_info = r.json() if r.ok else {}
                        except:
                            pass

                        request.session["user_email"] = email
                        request.session["user_first_name"] = user_info.get("first_name", "")
                        request.session["user_last_name"] = user_info.get("last_name", "")

                        return redirect("/user-organizations/")

        elif stage == "complete_profile":
            missing = []
            if not first_name:
                missing.append("first_name")
            if not last_name:
                missing.append("last_name")
            if not church:
                missing.append("church")
            if missing:
                ctx.update({
                    "show_new_user_fields": True,
                    "button_text": "Complete Account",
                    "message": "Please complete all fields.",
                    "message_class": "error",
                    "email": email,
                    "readonly_email": True,
                })
            else:
                payload = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "church": church,
                    "schedulebuddy": {"organizations": []},
                }
                r = requests.put(f"{API_BASE}/users/{email}", json=payload)
                if not r.ok:
                    detail = r.json().get("detail", "Failed to complete profile.")
                    ctx.update({
                        "show_new_user_fields": True,
                        "button_text": "Complete Account",
                        "message": detail,
                        "message_class": "error",
                        "email": email,
                        "readonly_email": True,
                    })
                else:
                    ctx.update({
                        "message": "Account created and profile updated!",
                        "message_class": "success",
                    })
                    user_info = {}
                    try:
                        r2 = requests.get(f"{API_BASE}/users/{email}")
                        user_info = r2.json() if r2.ok else {}
                    except:
                        pass

                    request.session["user_email"] = email
                    request.session["user_first_name"] = user_info.get("first_name", "")
                    request.session["user_last_name"] = user_info.get("last_name", "")

                    return redirect("/user-organizations/")

    ctx["stage"] = stage
    return render(request, "login.html", ctx)


def user_organizations_view(request):
    user_email = request.session.get("user_email", "")
    first_name = request.session.get("user_first_name", "")
    last_name = request.session.get("user_last_name", "")

    if not user_email:
        return redirect("login")

    user_data = {}
    try:
        resp_user = requests.get(f"{API_BASE}/users/{user_email}")
        if resp_user.ok:
            user_data = resp_user.json()
        else:
            user_data = {}
    except requests.RequestException:
        user_data = {}

    org_ids = user_data.get("schedulebuddy", {}).get("organizations", []) or []

    orgs_full = []
    for oid in org_ids:
        try:
            resp_org = requests.get(f"{API_BASE}/schedulebuddy/organizations/{oid}")
            if resp_org.ok:
                od = resp_org.json()
                orgs_full.append({
                    "name": od.get("name", "(no name)"),
                    "id": od.get("_id", oid),
                })
            else:
                orgs_full.append({
                    "name": "(failed to load)",
                    "id": oid,
                })
        except requests.RequestException:
            orgs_full.append({
                "name": "(network error)",
                "id": oid,
            })

    context = {
        "user_email": user_email,
        "first_name": first_name,
        "last_name": last_name,
        "orgs": orgs_full,
    }

    return render(request, "user-organizations.html", context)


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