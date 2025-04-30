# ScheduleBuddy/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class EmailForm(forms.Form):
    email = forms.EmailField()

class OTPForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    otp = forms.CharField(max_length=10)

class NewUserForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    church = forms.CharField(max_length=100)

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'church')  # Include fields for role and church

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password'
        })
    )