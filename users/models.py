"""Custom user model."""
from __future__ import annotations

import uuid
from typing import Any

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from bitfield import BitField
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nutrition_tracker.models import db_base


class UserManager(BaseUserManager):
    """Extend BaseUserManager for custom User model."""

    use_in_migrations = True

    def _create_user(self, email: str | None, password: str | None, **extra_fields: Any) -> User:
        """
        Create and save a user with the given email, and password.
        """
        email = self.normalize_email(email)
        user: User = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> User:
        """
        Create and save a user with the given email, and optional password.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str | None = None, password: str | None = None, **extra_fields: Any) -> User:
        """
        Create and save a superuser.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, db_base.DbBase):
    """Custom User Model."""

    FLAG_IS_PREGNANT = "is_pregnant"

    id = models.BigAutoField(primary_key=True)
    external_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="external_id",
        help_text="External UUID for the user.",
    )
    first_name = models.CharField(_("First Name"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("Last Name"), max_length=150, blank=True, null=True)
    email = models.EmailField(_("Email Address"), unique=True)
    date_of_birth = models.DateField(
        blank=True, null=True, verbose_name="date_of_birth", help_text="User's date of birth."
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    family_id = models.UUIDField(
        blank=True, null=True, verbose_name="family_id", help_text="UUID of the family the user belongs to."
    )
    family_added_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="family_added_timestamp",
        help_text="Timestamp when the user was added to a family.",
    )
    flags = BitField(flags=(FLAG_IS_PREGNANT,), null=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )

    class Meta(db_base.DbBase.Meta):
        db_table = "ut_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(name="user_familyid_idx", fields=["family_id"]),
        ]

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__original_family_id = self.family_id

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.__original_family_id != self.family_id:
            self.family_added_timestamp = timezone.now()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self) -> str:
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self) -> str | None:
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject: str, message: str, from_email: str | None = None, **kwargs: Any) -> None:
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def add_email(self, new_email: str) -> Any:
        """Add a new email address for the user, and send verification email.
        Old email will remain primary until the new email is confirmed."""
        return EmailAddress.objects.add_email(None, self, new_email, confirm=True)

    def __str__(self) -> str:
        return self.get_short_name() or self.email

    def get_flag(self, name: str) -> bool:
        """Get flag value."""
        return getattr(self.flags, name)

    def add_flag(self, name: str) -> None:
        """Add flag value."""
        self.flags |= getattr(self.__class__.flags, name)

    def remove_flag(self, name: str) -> None:
        """Remove flag value."""
        self.flags &= ~getattr(self.__class__.flags, name)

    def update_flag(self, name: str, value: bool) -> None:
        """Update flag value."""
        if value:
            self.add_flag(name)
        else:
            self.remove_flag(name)

    def is_pregnant(self) -> bool:
        """Return FLAG_IS_PREGNANT value."""
        return self.flags.is_pregnant.is_set


@receiver(email_confirmed)
def update_user_email(sender: str, request: HttpRequest, email_address: Any, **kwargs: Any) -> None:
    """Update primary email address once the email is confirmed.
    Delete old email addresses."""
    del sender  # unused
    email_address.set_as_primary()
    EmailAddress.objects.filter(user=email_address.user).exclude(primary=True).delete()
