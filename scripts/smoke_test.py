import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')
django.setup()

from django.contrib.auth import get_user_model
from groups.models import Group, GroupMembership
from accounts.models import Subscriber
from posts.models import Post
from core.models import Notification

User = get_user_model()

u1, created1 = User.objects.get_or_create(username='testuser1', defaults={'email':'t1@example.com'})
print('u1 created', created1)

u2, created2 = User.objects.get_or_create(username='testuser2', defaults={'email':'t2@example.com'})
print('u2 created', created2)

s, created3 = Subscriber.objects.get_or_create(from_user=u2, to_user=u1)
print('subscription created', created3)

g, created4 = Group.objects.get_or_create(name='Test Group')
print('group created', created4)

gm, created5 = GroupMembership.objects.get_or_create(user=u1, group=g, defaults={'role':'admin'})
print('membership created', created5)

p = Post.objects.create(author=u1, content='Group post', group=g)
print('post created', p.pk)

qs = Notification.objects.filter(recipient=u2)
print('notifications for u2:', qs.count())
for n in qs:
    print(n.verb, 'from actor id', getattr(n.actor, 'id', None))
