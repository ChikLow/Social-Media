from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Group(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through="GroupMembership")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    allow_public_posts = models.BooleanField(default=True, help_text='Allow any authenticated user to post in this group')

    def get_absolute_url(self):
        from django.urls import reverse
        # fallback to pk when slug missing
        slug = self.slug if self.slug else self.pk
        return reverse('group_detail', kwargs={'slug': slug})

    def save(self, *args, **kwargs):
        # ensure slug exists and is unique
        from django.utils.text import slugify
        if not self.slug:
            base = slugify(self.name) if self.name else 'group'
            slug = base
            counter = 1
            while Group.objects.filter(slug=slug).exclude(pk=getattr(self, 'pk', None)).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[("member", "Member"), ("admin", "Admin")])
    joined_at = models.DateTimeField(auto_now_add=True)
