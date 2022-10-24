from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
import datetime 

# Create your views here.

def index(request):
    template = 'posts/index.html'
    title = 'Это главная страница проекта Yatube'
    posts_list = Post.objects.order_by('-pub_date').select_related('group').select_related('author')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title' : title,
        'page_obj' : page_obj,
    }
    return HttpResponse(render(request, template, context))


def search(request):
    keyword = request.GET.get("q", None)
    if keyword:
        posts = Post.objects.filter(text__contains=keyword).select_related('author').select_related('group')
    else:
        posts = None
    return render(request, "search.html", {"posts": posts, "keyword": keyword})


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = (Post.objects.filter(group=group)
                  .order_by('-pub_date')
                  .select_related('group')
                  .select_related('author')
                  )
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    context = {
        'group' : group,
        'page_obj' : page_obj,
    }
    return HttpResponse(render(request, template, context))


def profile(request, username):
    user_author = User.objects.get(username=username)
    posts = (Post.objects.select_related('group')
             .select_related('author')
             .filter(author_id=user_author.pk)
             .order_by('-pub_date')
             )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user_author':user_author,
        'posts':posts,
        'page_obj':page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = (Post.objects
            .prefetch_related('author')
            .prefetch_related('group')
            .get(pk=post_id)
            )
    count_posts = Post.objects.filter(author_id=post.author.pk).count()
    context = {
        'post':post,
        'count':count_posts
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            complite = form.save(commit=False)
            complite.author = request.user
            print('кааак тааак')
            complite.save()
            return redirect('/profile/'+str(request.user))
        return render(request, 'posts/create_post.html', {'form':form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form':form})


def post_edit(request, post_id):
    post = Post.objects.select_related('author').get(pk=post_id)
    if request.method == 'GET':
        is_edit = True
        #if post.author_id == User.objects.get(username=request.user).pk: первый варинт проверки на проверку что редактирует автор, далее проверю какой вариант меньше грузит базу
        if post.author == request.user:
            form = PostForm(instance=post) # вставить в форму пост для редактирования
            return render(request, 'posts/create_post.html', {'form':form, 'is_edit':is_edit, 'post_id':post_id})
        return redirect('/auth/login/')
    form = PostForm(request.POST, instance = post) # instance переопределяет параметры которые не вошли в пост запрос, в коде ниже второй вариант передачи параметров
    if form.is_valid():
        complite = form.save(commit=False)
        #complite.author = request.user
        #complite.pk = post.pk
        #complite.pub_date = post.pub_date
        #complite.save()
        print('gfgfgfgfgfg')
        return redirect('/profile/'+str(request.user))
    return render(request,'posts/create_post.html', {'form':form, 'is_edit':is_edit, 'post_id':post_id}, ) #пользователь переделывает форму, она не валид