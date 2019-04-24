import traceback

import sys

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now as django_now
from auprico_core.models import Person, Email

# Create your models here.
from django.db.models import PROTECT
from django.utils.translation import ugettext_lazy


# django-admin.py makemigrations auprico_auth --settings=test_settings


class User(Person, AbstractUser):
    edited_by = models.ForeignKey("User", on_delete=PROTECT, null=True, related_name="edited_users")


class UserEmail(Email):
    user = models.ForeignKey(User, on_delete=PROTECT, related_name="emails")
    edited_by = models.ForeignKey(User, on_delete=PROTECT, related_name="edited_emails")
