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

class FeedView(ListView):
    model = Post
    template_name = 'posts/feed.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related('media','likes','comments').order_by('-created_at')
    
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