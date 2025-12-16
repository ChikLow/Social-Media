from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Post(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey('groups.Group', null=True, blank=True, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True)
    # залишаємо image якщо потрібно, але використовуємо PostMedia для мульти-медіа
    # image = models.ImageField(upload_to="posts/", blank=True, null=True)

    def __str__(self):
        return f"Post by {self.author}"

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()


class PostMedia(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='posts/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"Comment by {self.author}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} likes {self.post}"
