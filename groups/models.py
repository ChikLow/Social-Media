from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Group(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through="GroupMembership")

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[("member", "Member"), ("admin", "Admin")])
    joined_at = models.DateTimeField(auto_now_add=True)
