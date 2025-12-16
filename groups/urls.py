from django.urls import path
from . import views

urlpatterns = [
    path('', views.GroupListView.as_view(), name='groups_list'),
    path('create/', views.GroupCreateView.as_view(), name='group_create'),
    path('<slug:slug>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('<slug:slug>/join/', views.JoinGroupView.as_view(), name='group_join'),
    path('<slug:slug>/leave/', views.LeaveGroupView.as_view(), name='group_leave'),
]
