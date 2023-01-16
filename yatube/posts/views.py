from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required


# Create your views here.


def index(request):
    template = 'posts/index.html'
    posts_list = (
        Post.objects.order_by('-pub_date')
        .select_related('group')
        .select_related('author')
    )
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'req_user': request.user,
        'page_obj': page_obj,
    }
    return HttpResponse(render(request, template, context))


def search(request):
    keyword = request.GET.get("q", None)
    if keyword:
        posts = (
            Post.objects.filter(text__contains=keyword)
            .select_related('author')
            .select_related('group')
        )
    else:
        posts = None
    return render(request, "search.html", {"posts": posts, "keyword": keyword})


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = (
        Post.objects.filter(group=group)
        .order_by('-pub_date')
        .select_related('group')
        .select_related('author')
    )
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    context = {
        'req_user': request.user,
        'group': group,
        'page_obj': page_obj,
    }
    return HttpResponse(render(request, template, context))


def profile(request, username):
    user_author = get_object_or_404(User, username=username)
    # posts = user_author.author.all() либо попробывать так
    posts = (
        Post.objects.select_related('group')
        .select_related('author')
        .filter(author_id=user_author.pk)
        .order_by('-pub_date')
    )
    #  проверим есть ли подписка пользователя на автора страницы
    following = Follow.objects.filter(user=request.user, author=user_author).exists()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_count = posts.count()
    context = {
        'req_user': request.user,
        'user_author': user_author,
        'post_count': post_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    if Post.objects.filter(pk=post_id).exists():
        post = (
            Post.objects
            .select_related('author')
            .select_related('group')
            .get(pk=post_id)
        )
        count_posts = Post.objects.filter(author_id=post.author.pk).count()
        comments = Comment.objects.filter(post=post_id)
        form = CommentForm()
        context = {
            'req_user': request.user,
            'post': post,
            'count': count_posts,
            'form': form,
            'comments': comments,
        }
        return render(request, 'posts/post_detail.html', context)
    raise Http404()


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            complite = form.save(commit=False)
            complite.author = request.user
            complite.save()
            return redirect('posts:profile', username=request.user)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    if Post.objects.filter(pk=post_id).exists():
        post = Post.objects.select_related('author').get(pk=post_id)
        if request.method == 'GET':
            is_edit = True
            if post.author == request.user:
                # вставить в форму пост для редактирования
                form = PostForm(
                    instance=post,
                    files=request.FILES or None
                ) 
                return render(request, 'posts/create_post.html', {'form': form, 'is_edit': is_edit, 'post_id': post_id})
            return redirect('/auth/login/')
        # instance переопределяет параметры которые не вошли в пост запрос, в коде ниже второй вариант передачи параметров
        form = PostForm(
            request.POST,
            instance=post,
            files=request.FILES or None
        )
        if form.is_valid():
            complite = form.save(commit=False)
            #complite.author = request.user 
            #complite.pk = post.pk
            #complite.pub_date = post.pub_date
            complite.save()
            return redirect('posts:profile', username=request.user)
        return render(request,'posts/create_post.html', {'form': form, 'is_edit': is_edit, 'post_id': post_id}, ) #пользователь переделывает форму, она не валид
    return Http404()


def delite_post(request, post_id): 
    try:
        post = Post.objects.select_related('author').get(pk=post_id)
        if post.author == request.user:
            post.delete()
    finally:
        return redirect('posts:home_page')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


def follow_index(request):
    try:
        authors = Follow.objects.filter(user=request.user)
        #  создадим пустой qweryset
        posts = Post.objects.none()
        #  в цикле объеденим его с множествами постов по подписанным авторам   
        for author in authors:
            QS = Post.objects.select_related('author').filter(author=author.author)
            posts = posts.union(QS)
        paginator = Paginator(posts.order_by('-pub_date'), 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'posts/follow.html', {'page_obj':page_obj})
    except:
        raise Http404()


@login_required
def profile_follow(request, username):
    try:
        follow_obj = Follow.objects.create(user=request.user, author=User.objects.get(username=username))
        follow_obj.save()
        return redirect('posts:profile', username=username)
    except:
        raise Http404()

@login_required
def profile_unfollow(request, username):
    try:
        follow_obj = Follow.objects.filter(user=request.user, author=User.objects.get(username=username))
        follow_obj.delete()
        return redirect('posts:profile', username=username)
    except:
        raise Http404()