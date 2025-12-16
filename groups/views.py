from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, View
from .models import Group, GroupMembership
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django import forms


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'slug', 'description', 'allow_public_posts']


from django.db.models import Exists, OuterRef, Value, BooleanField

class GroupListView(ListView):
    model = Group
    template_name = 'groups/list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            membership_qs = GroupMembership.objects.filter(group=OuterRef('pk'), user=user)
            qs = qs.annotate(is_member=Exists(membership_qs))
        else:
            qs = qs.annotate(is_member=Value(False, output_field=BooleanField()))
        return qs


class GroupDetailView(DetailView):
    model = Group
    template_name = 'groups/detail.html'
    context_object_name = 'group'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        posts = group.posts.select_related('author').prefetch_related('media','likes','comments').order_by('-created_at')
        context['posts'] = posts
        user = self.request.user
        context['is_member'] = False
        if user.is_authenticated:
            context['is_member'] = group.members.filter(id=user.id).exists()
        return context


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'groups/create.html'

    def form_valid(self, form):
        group = form.save()
        # make creator an admin
        GroupMembership.objects.create(user=self.request.user, group=group, role='admin')
        return redirect(group.get_absolute_url())


class JoinGroupView(LoginRequiredMixin, View):
    def post(self, request, slug):
        group = get_object_or_404(Group, slug=slug)
        if group.members.filter(id=request.user.id).exists():
            return redirect(group.get_absolute_url())
        GroupMembership.objects.create(user=request.user, group=group, role='member')
        return redirect(group.get_absolute_url())


class LeaveGroupView(LoginRequiredMixin, View):
    def post(self, request, slug):
        group = get_object_or_404(Group, slug=slug)
        m = GroupMembership.objects.filter(user=request.user, group=group).first()
        if m:
            m.delete()
        return redirect(group.get_absolute_url())
from django.shortcuts import render

# Create your views here.
