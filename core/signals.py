from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from accounts.models import Subscriber
from posts.models import Like, Comment, Post
from .models import Notification


@receiver(post_save, sender=Subscriber)
def create_follow_notification(sender, instance, created, **kwargs):
    if not created:
        return
    # from_user started following to_user
    actor = instance.from_user
    recipient = instance.to_user
    if actor == recipient:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb='started following you',
        data={'from_user_id': actor.id}
    )


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if not created:
        return
    post = instance.post
    actor = instance.user
    recipient = post.author
    if actor == recipient:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb='liked your post',
        target_content_type=ContentType.objects.get_for_model(post),
        target_object_id=str(post.id),
        data={'post_id': post.id}
    )


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if not created:
        return
    post = instance.post
    actor = instance.author
    recipient = post.author
    if actor == recipient:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb='commented on your post',
        target_content_type=ContentType.objects.get_for_model(post),
        target_object_id=str(post.id),
        data={'post_id': post.id, 'comment_id': instance.id, 'text': instance.content[:200]}
    )


@receiver(post_save, sender=Post)
def create_post_notifications(sender, instance, created, **kwargs):
    if not created:
        return
    author = instance.author
    # notify followers
    followers = Subscriber.objects.filter(to_user=author).select_related('from_user')
    ctype = ContentType.objects.get_for_model(instance)
    notifications = []
    for s in followers:
        recipient = s.from_user
        if recipient == author:
            continue
        notifications.append(Notification(
            recipient=recipient,
            actor=author,
            verb='posted a new post',
            target_content_type=ctype,
            target_object_id=str(instance.id),
            data={'post_id': instance.id}
        ))
    if notifications:
        Notification.objects.bulk_create(notifications)
