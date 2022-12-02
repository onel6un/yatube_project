from django.test import TestCase, Client
from ..models import *
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
import time
User = get_user_model()

class ViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_u') #'Просто авторизированный пользователь'
        cls.user_author = User.objects.create(username='test_a') # юзер - автор тестогово поста
        cls.user_not_follow = User.objects.create(username='test_us_unfoll') # юзер - не подписанный на никого
        cls.user_follow = User.objects.create(username='test_us_foll')  # юзер - подписанный на cls.user_author
        cls.group = Group.objects.create(
            title = 'Тестовый заголовок группы',
            slug = 'slug-test',
            description = 'Тестовое описание'
        )
        cls.post = Post.objects.create(
            text = 'Тестовый текст',
            author = ViewsTests.user_author,
            group = ViewsTests.group
        )
        cls.follow_user_author = Follow.objects.create(
            user = ViewsTests.user_follow,
            author = ViewsTests.user_author
        )

        

    def setUp(self):
        self.guest_client = Client() #не авторизированный клиент
        self.auth_client = Client()
        self.auth_client.force_login(ViewsTests.user) # авторизированный клиент, но не автор поста
        self.author_client = Client()
        self.author_client.force_login(ViewsTests.user_author) #клиент авторизированный автором поста
        self.user_not_follow_client = Client()
        self.user_not_follow_client.force_login(ViewsTests.user_not_follow)
        self.user_follow_client = Client()
        self.user_follow_client.force_login(ViewsTests.user_follow)


    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_names = {
            reverse('posts:home_page'): 'posts/index.html',
            reverse('posts:create'): 'posts/create_post.html',
            (reverse('posts:edit', kwargs={'post_id': '1'})): 'posts/create_post.html',
            (reverse('posts:post_detail', kwargs={'post_id': '1'})): 'posts/post_detail.html',
            (reverse('posts:profile', kwargs={'username': 'test_a'})): 'posts/profile.html',
            (reverse('posts:group_list', kwargs={'slug': 'slug-test'})): 'posts/group_list.html',
        }
        for reverse_name, template in template_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        response = self.auth_client.get(reverse('posts:home_page'))
        second_obj = response.context['page_obj'][0]
        post_text = second_obj.text
        post_author = second_obj.author
        post_group_title = second_obj.group.title
        self.assertEqual(post_text, ViewsTests.post.text)  # вторым аргументом передали объект класса Пост, 
                                                        # тект которого мы ожидаем в качестве контекста
        self.assertEqual(post_author, ViewsTests.post.author) 
        self.assertEqual(post_group_title, ViewsTests.post.group.title)

    def test_group_list_show_correct_and_sorted_context(self):
        sent_slug = 'slug-test'
        response = (self.auth_client.
            get(reverse('posts:group_list', kwargs={'slug': sent_slug})))
        page_obj = response.context['page_obj'][0]  # извлекаем из словаря контекста первый пост
        self.assertEqual(page_obj.group.slug, sent_slug)  # слаг группы поста размещенного на странице соответствует, переданному в url
        
    def test_profile_show_posts_author_list_correct(self):
        sent_username = 'test_a' # username автора постов
        response = (self.auth_client.
            get(reverse('posts:profile', kwargs={'username': sent_username}))) # получаем response для страницы профиля автора
        page_obj = response.context['page_obj'][0] #извлекаем из словаря контекста первый пост
        self.assertEqual(page_obj.author.username, sent_username) # в качестве элемента словаря контекста на стрицу передаеться,
                                                                   # экземляр класса post отсортированный по username, переданному через slug
    
    def test_post_detail_show_one_post(self):
        sent_post_id = 1 # post_id поста
        response = (self.auth_client.
            get(reverse('posts:post_detail', kwargs={'post_id': sent_post_id}))) # получаем response для страницы профиля автора
        page_obj = response.context['post'] #выводим все посты, ожидаеться что он будет один
        self.assertEqual(page_obj.pk, sent_post_id) # id выведенного поста соответсвует ожидаемому
        self.assertEqual(len([page_obj]), 1) # пост передаеться в контекст, один единственны
        
    def test_form_edit_post(self):
        sent_post_id = 1
        response = (self.author_client.
            get(reverse('posts:edit', kwargs={'post_id': sent_post_id})))

        form_obj = response.context.get('form')
        self.assertEqual(form_obj.instance.pk, sent_post_id) # instance атрибут класса ModelForm в который мы передавали Объект класса Post,
                                                            # редактироваться будет тот Пост pk которого мы передали в url

    def test_create_post_context(self):
        response = (self.auth_client.
            get(reverse('posts:create')))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertEqual(expected, type(form_field))
    
    
    def test_follows_and_unfollows(self):
        '''проверяем функции представлений подписки и отписки от авторов'''
        #  посчитаем количество записей модели Follow с полем user = ViewsTests.user
        count_follow = Follow.objects.filter(user=ViewsTests.user).count()
        #  подпишемся на посты ViewsTests.user_author
        response = self.auth_client.get(reverse('posts:profile_follow', kwargs={'username': ViewsTests.user_author.username}))
        self.assertEqual = (count_follow+1, Follow.objects.filter(user=ViewsTests.user).count(), 'подписка не работает')
        count_follow_bef_unfoll = Follow.objects.filter(user=ViewsTests.user).count()
        response = self.auth_client.get(reverse('posts:profile_unfollow', kwargs={'username': ViewsTests.user_author.username}))
        self.assertEqual = (count_follow_bef_unfoll, Follow.objects.filter(user=ViewsTests.user).count(), 'отписка не работает')


    def test_follow_index_show_posts(self):
        '''Функция представления follow_index, показывает подписаннымм на авторов,
        их посты'''
        response = self.user_follow_client.get(reverse('posts:follow_index'))
        post1 = response.context['page_obj'][0]
        # проверим что в контект страницы передаеться текст поста автора на которого подписан автор
        self.assertEqual(post1.text, 'Тестовый текст')


    def test_follow_index_not_show_posts(self):
        '''Функция представления follow_index, не показывает неподписаннымм на авторов,
        их посты'''
        response = self.user_not_follow_client.get(reverse('posts:follow_index'))
        posts = response.context['page_obj'].object_list
        # проверим что в контект страницы передаеться пустое множество, тк юзер ни накого не подписан
        self.assertEqual(len(posts), 0)


class ViewsPaginatorTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_u') #'Просто авторизированный пользователь'
        cls.user_author = User.objects.create(username='test_a') # юзер - автор тестогово поста
        cls.user_author2 = User.objects.create(username='test_a2') # юзер - автор тестогово поста
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='slug-test',
            description='Тестовое описание'
        )
        #создадим вторую группу для проверки размещения постов по группам
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок группы2',
            slug='slug-test2',
            description='Тестовое описание'
        )
        cls.post2=Post.objects.create(
            text='Тестовый текст второго автора',
            author=ViewsPaginatorTests.user_author2,
            group=ViewsPaginatorTests.group2
        )
        
        for i in range(15):
            Post.objects.create(
                text = 'Тестовый текст'+str(15),
                author = ViewsPaginatorTests.user_author,
                group = ViewsPaginatorTests.group
            )

        
    def setUp(self):
        self.guest_client = Client() #не авторизированный клиент
        self.auth_client = Client()
        self.auth_client.force_login(ViewsPaginatorTests.user) # авторизированный клиент, но не автор поста
        self.author_client = Client()
        self.author_client.force_login(ViewsPaginatorTests.user_author) #клиент авторизированный автором поста   
        self.author2_client = Client()
        self.author2_client.force_login(ViewsPaginatorTests.user_author2) #клиент второго авторф 


    def test_paginator_on_home_page(self):
        """На одну страницу выводиться не больше 10 постов"""
        response = self.auth_client.get(reverse('posts:home_page'))
        obj_list = response.context['page_obj']
        self.assertEqual(len(obj_list), 10)


    def test_paginator_second_page_on_home_page(self):
        """На второй странице должно быть 5 постов"""
        response = self.auth_client.get(reverse('posts:home_page')+'?page=2')
        obj_list = response.context['page_obj']
        self.assertEqual(len(obj_list), 6)


    def test_paginator_on_group_list(self):
        """На одну страницу выводиться не больше 10 постов"""
        response = (self.auth_client.
            get(reverse('posts:group_list', kwargs={'slug': 'slug-test'})))
        obj_list = response.context['page_obj']
        self.assertEqual(len(obj_list), 10)


    def test_paginator_second_page_on_group_list(self):
        """На второй странице должно быть 5 постов"""
        response = (self.auth_client.
            get(reverse('posts:group_list', kwargs={'slug': 'slug-test'})+'?page=2'))
        obj_list = response.context['page_obj']
        self.assertEqual(len(obj_list), 5)


    def test_paginator_on_profile(self):
        """На одну страницу выводиться не больше 10 постов"""
        username = ViewsPaginatorTests.user_author.username
        response = (self.auth_client.
            get(reverse('posts:profile', kwargs={'username': username})))
        obj_list = response.context['page_obj']
        self.assertEqual(len(obj_list), 10)


    def test_paginator_second_page_on_profile(self):
        """На второй странице должно быть 5 постов"""
        username = ViewsPaginatorTests.user_author.username
        response = (self.auth_client.
            get(reverse('posts:profile', kwargs={'username': username})+'?page=2'))
        obj_list = response.context['page_obj']
        self.assertEqual(len(obj_list), 5)


    def test_one_post_on_profile_second_author(self):
        """На странице должно быть 1 единственный пост второго автора """
        username = ViewsPaginatorTests.user_author2.username
        response = (self.auth_client.
            get(reverse('posts:profile', kwargs={'username': username})))
        obj_list = response.context['page_obj']
        self.assertEqual(len(obj_list), 1)


    def test_one_post_on_group_list_second_group(self):
        """На странице должно быть 1 единственный пост второй группы """
        slug2 = ViewsPaginatorTests.post2.group.slug
        response = (self.auth_client.
            get(reverse('posts:group_list', kwargs={'slug': slug2})))
        obj_list = response.context['page_obj']
        self.assertEqual(len(obj_list), 1)

    
    def test_error_page(self):
        '''Проверка сраницы ощибки 404err'''
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        template = 'core/404.html'
        self.assertTemplateUsed(response, template) # используется шаблон core/404.html


class CacheTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_u') #'Просто авторизированный пользователь'
        cls.user_author = User.objects.create(username = 'test_a') # юзер - автор тестогово поста
        cls.post = Post.objects.create(
            text = 'Тестовый текст',
            author = CacheTests.user_author,
        )
        

    def setUp(self):
        self.guest_client = Client() #не авторизированный клиент
        self.auth_client = Client()
        self.auth_client.force_login(CacheTests.user) # авторизированный клиент, но не автор поста


    def test_cache(self):
        '''Тестируем кеширование'''
        response = self.guest_client.get(reverse('posts:home_page'))
        CacheTests.post = Post.objects.create(
            text = 'Тестовый текст2',
            author = CacheTests.user_author,
        )
        response1 = self.guest_client.get(reverse('posts:home_page'))
        #  после обнавления базы данных пользователю показывают прежнию страницу загруженную из кеша
        self.assertEqual(response.content, response1.content) 
        time.sleep(20)
        # после 20 секундного ожидания кеш очищаеться и пост появляеться на странице
        response3 = self.guest_client.get(reverse('posts:home_page'))
        self.assertNotEqual(response.content, response3.content)
