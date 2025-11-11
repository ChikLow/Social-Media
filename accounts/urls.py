from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import RegisterView, ProfileUpdateView, UserLoginView
from django.conf.urls.static import static
from django.conf import settings
from . import views


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/edit', ProfileUpdateView.as_view(), name='edit_profile'),
    path('search/', views.account_search, name='account_search'),
    path('subscribe/<int:user_id>/', views.subscribe, name='subscribe'),
]
