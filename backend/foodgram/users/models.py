from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.constants import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_F_NAME,
    MAX_LENGTH_L_NAME,
    MAX_LENGTH_USERNAME,
)
from users.tools import normalize_avatar_path


class User(AbstractUser):
    username = models.CharField(
        _("username"), max_length=MAX_LENGTH_USERNAME, unique=True, blank=False
    )
    email = models.EmailField(
        _("email address"),
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        blank=False,
    )
    first_name = models.CharField(
        _("first name"),
        max_length=MAX_LENGTH_F_NAME,
        blank=False,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=MAX_LENGTH_L_NAME,
        blank=False,
    )
    avatar = models.ImageField(
        _("avatar"), upload_to=normalize_avatar_path, null=True, blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
