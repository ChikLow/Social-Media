from django.urls import path
from . import views

urlpatterns = [
    path('', views.FeedView.as_view(), name='feed'),
    path('create/', views.CreatePostView.as_view(), name='create_post'),
    path('<str:username>/posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/like/', views.toggle_like, name='toggle_like'),
]