from tokenize import group
from django.urls import include, path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='home_page'),
    path('group/<slug:slug>/', views.group_post, name='group_list'),
    path("search/", views.search, name="search"),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='create'),
    path('<int:post_id>/edit/', views.post_edit, name='edit'),
]