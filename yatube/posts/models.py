from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

# Create your models here.

User = get_user_model()

class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add = True)
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
        null=True
    )

    def __str__(self) -> str:
        return self.text

class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200,)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        return reverse("group_list", kwargs={"slug": self.slug})
    
