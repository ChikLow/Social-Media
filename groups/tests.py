from django.test import TestCase
from django.contrib.auth import get_user_model
from groups.models import Group, GroupMembership
from accounts.models import Subscriber
from posts.models import Post
from core.models import Notification


class GroupNotificationTest(TestCase):
    def test_post_creates_notification_for_followers(self):
        User = get_user_model()
        u1 = User.objects.create_user(username='u1', password='pass')
        u2 = User.objects.create_user(username='u2', password='pass')
        Subscriber.objects.create(from_user=u2, to_user=u1)
        g = Group.objects.create(name='Test Group')
        GroupMembership.objects.create(user=u1, group=g, role='admin')
        p = Post.objects.create(author=u1, content='Group Post', group=g)
        self.assertTrue(Notification.objects.filter(recipient=u2, actor=u1, verb='posted a new post').exists())

    def test_group_create_generates_slug_and_redirects(self):
        User = get_user_model()
        u = User.objects.create_user(username='creator', password='pass')
        self.client.login(username='creator', password='pass')
        resp = self.client.post('/groups/create/', {'name': 'Hello Group', 'description': 'desc'}, follow=True)
        # should redirect to group detail
        self.assertEqual(resp.status_code, 200)
        g = Group.objects.get(name='Hello Group')
        self.assertIsNotNone(g.slug)
        self.assertIn(g.slug, resp.request['PATH_INFO'])


