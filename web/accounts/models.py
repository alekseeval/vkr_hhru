from django.db import models

# Create your models here.

from django.contrib.auth.models import User


class HhUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.TextField()
    hh_id = models.TextField(unique=True, default=None)
    access_token = models.TextField()
    refresh_token = models.TextField()

    def __str__(self):
        return f'{self.user.first_name} {self.middle_name}'
