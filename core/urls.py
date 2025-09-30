from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import ProfileDetailView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('profile/<int:pk>', ProfileDetailView.as_view(), name='profile_detail'),
]
