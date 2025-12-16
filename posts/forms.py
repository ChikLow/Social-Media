from django import forms
from .models import Post
from groups.models import Group

class PostForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False, label='Group (optional)')
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "what's on your mind today?",
                'rows': 3
            })
        }