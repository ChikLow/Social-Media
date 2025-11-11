from django.shortcuts import render
from accounts.models import User
from django.views.generic import DetailView

# Create your views here.
class ProfileDetailView(DetailView):
    template_name = 'core/profile.html'
    model = User
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        # Отримуємо підписників/підписки через модель Subscriber
        from accounts.models import Subscriber

        # Subscribers where to_user == profile -> люди, що підписані на профіль
        followers_qs = Subscriber.objects.filter(to_user=profile).select_related('from_user')
        # Subscribers where from_user == profile -> на кого підписаний профіль
        following_qs = Subscriber.objects.filter(from_user=profile).select_related('to_user')

        followers = [s.from_user for s in followers_qs]
        following = [s.to_user for s in following_qs]

        # Спроба підвантажити пости (якщо в проєкті є модель Post)
        posts = []
        try:
            from posts.models import Post
            posts = Post.objects.filter(author=profile)
        except Exception:
            try:
                posts = profile.post_set.all()
            except Exception:
                posts = []

        context.update({
            'posts': posts,
            'followers': followers,
            'following': following,
            'followers_count': len(followers),
            'following_count': len(following),
        })
        return context