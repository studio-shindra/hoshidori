from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    display_name = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        db_table = 'accounts_user'

    def __str__(self):
        return self.username
