# models.py (update Meeting model to support recurring meetings)

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('minister', 'Minister'),
        ('user', 'User'),
        ('schedule_creator', 'Schedule Creator'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='user')
    church = models.CharField(max_length=255, blank=True, null=True)

class Ministry(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    church = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    assign_with_others = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Assignment(models.Model):
    ministry = models.ForeignKey(Ministry, related_name='assignments', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} (Qty: {self.quantity})"


class Meeting(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    recurring = models.BooleanField(default=False)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    ministries = models.ManyToManyField(Ministry, related_name='meetings', blank=True)

    def __str__(self):
        return f"{self.name} from {self.start_date} to {self.end_date}"

    @property
    def as_dict(self):
        return {
            'title': self.name,
            'start': self.start_date.strftime('%Y-%m-%d'),
            'end': (self.end_date + timedelta(days=1)).strftime('%Y-%m-%d'),
        }
