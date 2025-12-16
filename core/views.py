from django.shortcuts import render
from accounts.models import User
from django.views.generic import DetailView
from posts.models import Post
from posts.models import Like

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

        followers_qs = Subscriber.objects.filter(to_user=profile).select_related('from_user')
        following_qs = Subscriber.objects.filter(from_user=profile).select_related('to_user')

        followers = [s.from_user for s in followers_qs]
        following = [s.to_user for s in following_qs]

        # визначаємо чи поточний користувач підписаний на profile
        is_following = False
        request_user = getattr(self.request, 'user', None)
        if request_user and request_user.is_authenticated:
            is_following = Subscriber.objects.filter(from_user=request_user, to_user=profile).exists()

        # підвантажуємо пости автора
        posts = Post.objects.filter(author=profile).prefetch_related('media','likes','comments').order_by('-created_at')

        # позначаємо, які пости вже лайкнув поточний користувач
        if request_user and request_user.is_authenticated:
            liked_posts = set(Like.objects.filter(user=request_user).values_list('post_id', flat=True))
            for p in posts:
                p.is_liked_by_user = p.id in liked_posts
        else:
            for p in posts:
                p.is_liked_by_user = False

        context.update({
            'posts': posts,
            'followers': followers,
            'following': following,
            'followers_count': len(followers),
            'following_count': len(following),
            'is_following': is_following,
        })
        return context


# Notifications views
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 30

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-unread', '-created_at')

    def get(self, request, *args, **kwargs):
        # when user opens the list, mark all unread as read
        qs = self.get_queryset().filter(unread=True)
        qs.update(unread=False)
        return super().get(request, *args, **kwargs)


from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def mark_notification_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, recipient=request.user)
    n.mark_as_read()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('notifications')


@login_required
def notifications_dropdown(request):
    # return last 5 notifications and unread count
    last = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
    unread_count = Notification.objects.filter(recipient=request.user, unread=True).count()
    from django.template.loader import render_to_string
    html = render_to_string('notifications/_dropdown.html', {'notifications': last, 'user': request.user}, request=request)
    return JsonResponse({'html': html, 'unread_count': unread_count})