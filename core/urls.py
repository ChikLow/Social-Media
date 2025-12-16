from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import ProfileDetailView, NotificationListView, mark_notification_read, notifications_dropdown
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', mark_notification_read, name='mark_notification_read'),
    path('notifications/dropdown/', notifications_dropdown, name='notifications_dropdown'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
