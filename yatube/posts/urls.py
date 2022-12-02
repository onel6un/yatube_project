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
    path('posts/<int:post_id>/edit/', views.post_edit, name='edit'),
    path('delite/<int:post_id>', views.delite_post, name='delite'),
    path('posts/<int:post_id>/comment', views.add_comment, name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow, 
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name="profile_unfollow"
    ),
]
