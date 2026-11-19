from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Q


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password=password, **extra_fields)


class Company(models.Model):
    title = models.CharField(verbose_name="Company name", max_length=100)
    inn = models.CharField(unique=True, verbose_name="Taxpayer personal identification number", max_length=20)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.title


class Storage(models.Model):
    address = models.CharField(verbose_name="Company address", max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="Storage")

    def __str__(self):
        return f"{self.company} - storage address {self.address}"


class User(AbstractUser):
    # username = None
    username = models.CharField(unique=True, null=True, blank=True, verbose_name="User name", max_length=150)
    email = models.EmailField(unique=True, verbose_name="Email address", max_length=255)

    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    is_company_owner = models.BooleanField(default=False, verbose_name="Is company owner")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

        constraints = [
            models.UniqueConstraint(
                fields=["company"],
                condition=Q(is_company_owner=True),
                name="unique_company_owner"
            )
        ]

    def __str__(self):
        return self.email
