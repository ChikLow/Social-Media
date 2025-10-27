from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import RegisterView, ProfileUpdateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/edit', ProfileUpdateView.as_view(), name='edit_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
