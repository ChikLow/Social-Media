from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView
from django.urls import reverse_lazy,reverse
from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, UserProfileForm, LoginForm
from accounts.models import User, Subscriber
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404



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
    
def account_search(request):
    q = request.GET.get('q', '').strip()
    results = User.objects.none()
    if q:
        results = User.objects.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        ).distinct()
    context = {
        'query': q,
        'results': results,
    }
    return render(request, 'search_page.html', context)


@login_required
@require_POST
def subscribe(request, user_id):
    # не дозволяємо підписуватись на себе
    if request.user.id == user_id:
        return redirect('profile_detail', pk=user_id)
    user_to_subscribe = get_object_or_404(User, id=user_id)
    Subscriber.objects.get_or_create(from_user=request.user, to_user=user_to_subscribe)
    return redirect('profile_detail', pk=user_id)

@login_required
@require_POST
def unsubscribe(request, user_id):
    # не дозволяємо відписуватись від себе
    if request.user.id == user_id:
        return redirect('profile_detail', pk=user_id)
    user_to_unsubscribe = get_object_or_404(User, id=user_id)
    Subscriber.objects.filter(from_user=request.user, to_user=user_to_unsubscribe).delete()
    return redirect('profile_detail', pk=user_id)