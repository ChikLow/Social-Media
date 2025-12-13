from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .models import Post, PostMedia, Comment, Like
from .forms import PostForm
from django.http import Http404
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.db.models import Case, When, Value, IntegerField, Q

class FeedView(ListView):
    model = Post
    template_name = 'posts/feed.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        """
        Priority ordering:
         - 2: mutual friends (both follow each other)
         - 1: users current user follows
         - 0: everyone else
        Exclude current user's own posts.
        """
        qs = Post.objects.select_related('author').prefetch_related('media', 'likes', 'comments')

        user = getattr(self.request, 'user', None)

        if user and user.is_authenticated:
            # Avoid circular imports by importing inside function
            from accounts.models import Subscriber

            following_ids = list(Subscriber.objects.filter(from_user=user).values_list('to_user_id', flat=True))
            follower_ids = list(Subscriber.objects.filter(to_user=user).values_list('from_user_id', flat=True))
            friends_ids = set(following_ids).intersection(set(follower_ids))

            # Exclude the user's own posts
            qs = qs.exclude(author=user)

            # Annotate "priority" and order accordingly
            qs = qs.annotate(
                priority=Case(
                    When(author__id__in=list(friends_ids), then=Value(2)),
                    When(author__id__in=list(following_ids), then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ).order_by('-priority', '-created_at')
        else:
            # show everyone (or use qs.none() to hide for anonymous users)
            qs = qs.order_by('-created_at')

        return qs

    def render_to_response(self, context, **response_kwargs):
        """
        If this is an AJAX request (for pagination), return JSON containing the HTML slice,
        plus has_next boolean and next_page number for the frontend.
        """
        request = self.request
        page_obj = context.get('page_obj')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('posts/_posts_list.html', context=context, request=request)
            has_next = page_obj.has_next() if page_obj else False
            next_page = page_obj.next_page_number() if has_next else None
            return JsonResponse({
                'html': html,
                'has_next': has_next,
                'next_page': next_page
            })
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            liked_posts = set(Like.objects.filter(user=user).values_list('post_id', flat=True))
            for post in context['posts']:
                post.is_liked_by_user = post.id in liked_posts
        else:
            for post in context['posts']:
                post.is_liked_by_user = False
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        post = super().get_object()
        username = self.kwargs.get('username')
        if post.author.username != username:
            raise Http404("Post not found")
        return post

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['comments'] = self.object.comments.select_related('author').all()
        ctx['is_liked'] = False
        user = self.request.user
        if user.is_authenticated:
            ctx['is_liked'] = Like.objects.filter(post=self.object, user=user).exists()
        return ctx

class CreatePostView(LoginRequiredMixin, View):
    def get(self, request):
        form = PostForm()
        return render(request, 'posts/create_post.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        files = request.FILES.getlist('media')
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            for idx, f in enumerate(files):
                content_type = f.content_type.split('/')[0]
                media_type = 'image' if content_type == 'image' else 'video' if content_type == 'video' else 'image'
                PostMedia.objects.create(post=post, file=f, media_type=media_type, order=idx)
            return redirect('post_detail', username=post.author.username, pk=post.pk)
        return render(request, 'posts/create_post.html', {'form': form})

@login_required
def add_comment(request, post_id):
    if request.method != 'POST':
        return HttpResponseForbidden()
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content', '').strip()
    if content:
        Comment.objects.create(post=post, author=request.user, content=content)
    return redirect('post_detail', username=post.author.username, pk=post.id)

@login_required
def toggle_like(request, post_id):
    if request.method != 'POST':
        return HttpResponseForbidden()
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        is_liked = False
    else:
        is_liked = True
    
    # якщо AJAX запит — повернути JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_liked': is_liked,
            'like_count': post.like_count()
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'

    def get_success_url(self):
        return redirect("profile_detail", pk=self.request.user.id)

    def get_object(self):
        post = super().get_object()
        if post.author != self.request.user:
            raise Http404("You can't delete this post")
        return post

    def delete(self, request, *args, **kwargs):
        # AJAX delete без шаблону підтвердження
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            post = self.get_object()
            post.delete()
            return JsonResponse({'success': True})
        return super().delete(request, *args, **kwargs)