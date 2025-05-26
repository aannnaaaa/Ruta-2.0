from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'content', 'image', 'tags']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'content': 'Содержание',
            'image': 'Изображение',
            'tags': 'Теги',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название поста'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Краткое описание поста'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Текст поста'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'required': 'required'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Теги (через запятую)'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Размер изображения не должен превышать 5 МБ.')
        elif not self.instance.pk:  # Новый пост
            raise forms.ValidationError('Пожалуйста, загрузите изображение для поста.')
        return image