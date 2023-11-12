from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'comment_count', 'is_published', 'created_at')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
