from django import forms
from .models import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)

"""    def clean_group(self):
        data = self.cleaned_data['text']

        if data == '':
            raise forms.ValidationError('Это поле не должно быть пустым!')

        return data"""


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)