import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)

    # USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["phone_number"]

    class Meta:
        ordering = ("-date_joined",)

    def __str__(self):
        return self.phone_number


class UsersVerification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    validity = models.DateTimeField()
    valid = models.BooleanField(default=True)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return self.user.get_full_name()
