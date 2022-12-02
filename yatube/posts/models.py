from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

# Create your models here.

User = get_user_model()

class Post(models.Model):
    text = models.TextField(verbose_name='Текст', help_text='Введите текст')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name='group',
        blank=True, 
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    ) 

    def __str__(self) -> str:
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(verbose_name='Заголовок' ,max_length=200)
    slug = models.SlugField(verbose_name='URL адресс',max_length=200,)
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        return reverse("group_list", kwargs={"slug": self.slug})


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    def __str__(self) -> str:
        return self.author.username

