from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Користувач'),
        ('moderator', 'Модератор'),
        ('admin', 'Адміністратор'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Ім'я")
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Прізвище')
    bio = models.TextField(blank=True, verbose_name='Опис')
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name='Аватар', default="user.png")
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата народження')
    

    def __str__(self):
        return self.username
    

class Subscriber(models.Model):
    from_user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="followers")
    to_user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="follows")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')