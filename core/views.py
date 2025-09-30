from django.shortcuts import render
from accounts.models import User
from django.views.generic import DetailView

# Create your views here.
class ProfileDetailView(DetailView):
    template_name = 'core/profile.html'
    model = User
    context_object_name = "profile"