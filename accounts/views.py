from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView
from django.urls import reverse_lazy,reverse
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, UserProfileForm, LoginForm
from accounts.models import User



# Create your views here.
class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/edit_profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user
    
class UserLoginView(LoginView):
    template_name = 'auth_system/login.html'
    form_class = LoginForm

    def get_success_url(self):
        
        return reverse('profile_detail', args=[self.request.user.id])
    

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    login_url = 'login'  # якщо не залогінений — перекине сюди

    def get(self, request, *args, **kwargs):
        # якщо користувач намагається відкрити не свій профіль
        if request.user.id != int(self.kwargs['pk']):
            return redirect('profile', pk=request.user.id)
        return super().get(request, *args, **kwargs)