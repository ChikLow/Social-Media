from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import random

from groups.models import Group, GroupMembership
from posts.models import Post, Like, Comment
from accounts.models import Subscriber

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with users, groups, posts, likes and comments for testing'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of numeric users to create')
        parser.add_argument('--groups', type=int, default=3, help='Number of groups to create')
        parser.add_argument('--posts', type=int, default=10, help='Number of posts to create')
        parser.add_argument('--likes', type=int, default=20, help='Number of likes to create')
        parser.add_argument('--comments', type=int, default=20, help='Number of comments to create')

    def handle(self, *args, **options):
        users_n = options['users']
        groups_n = options['groups']
        posts_n = options['posts']
        likes_n = options['likes']
        comments_n = options['comments']

        created_users = []
        for i in range(1, users_n + 1):
            username = str(i)
            email = f"{i}@example.com"
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username=username, password=username, email=email)
                self.stdout.write(self.style.SUCCESS(f'Created user {username} / {username}'))
            else:
                u = User.objects.get(username=username)
                self.stdout.write(self.style.WARNING(f'User {username} exists'))
            created_users.append(u)

        created_groups = []
        for j in range(1, groups_n + 1):
            name = f"Group {j}"
            slug = slugify(name)
            g, created = Group.objects.get_or_create(name=name, defaults={'slug': slug})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Group {name} exists'))
            created_groups.append(g)
            # make user 1 admin if exists
            if created_users:
                try:
                    GroupMembership.objects.get_or_create(user=created_users[0], group=g, defaults={'role': 'admin'})
                except Exception:
                    pass
            # add a few members
            for member in random.sample(created_users, min(len(created_users), max(1, len(created_users)//2))):
                GroupMembership.objects.get_or_create(user=member, group=g, defaults={'role': 'member'})

        # create some follows so notifications will be generated
        for follower in created_users[1:]:
            Subscriber.objects.get_or_create(from_user=follower, to_user=created_users[0])

        created_posts = []
        for k in range(posts_n):
            author = random.choice(created_users)
            group = random.choice(created_groups + [None, None])  # more chance of no group
            p = Post.objects.create(author=author, content=f"Sample post {k+1} by {author.username}", group=group)
            created_posts.append(p)

        # likes
        for _ in range(likes_n):
            user = random.choice(created_users)
            post = random.choice(created_posts)
            try:
                Like.objects.get_or_create(user=user, post=post)
            except Exception:
                pass

        # comments
        for i in range(comments_n):
            user = random.choice(created_users)
            post = random.choice(created_posts)
            Comment.objects.create(author=user, post=post, content=f"Sample comment {i+1}")

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
        self.stdout.write(f'Created users: {len(created_users)}, groups: {len(created_groups)}, posts: {len(created_posts)}')
