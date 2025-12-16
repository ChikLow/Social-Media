import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')
django.setup()

from groups.models import Group

fixed = 0
for g in Group.objects.filter(slug__isnull=True):
    g.save()
    fixed += 1

print(f'Fixed {fixed} groups')
