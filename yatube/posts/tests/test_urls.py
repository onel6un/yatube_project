from django.test import TestCase, Client
from ..models import Post, Group
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_u') #'Просто авторизированный пользователь'
        cls.user_author = User.objects.create(username = 'test_a') # юзер - автор тестогово поста
        cls.group = Group.objects.create(
            title = 'Тестовый заголовок группы',
            slug = 'slug-test',
            description = 'Тестовое описание'
        )
        cls.post = Post.objects.create(
            text = 'Тестовый текст',
            author = StaticURLTests.user_author,
            group = StaticURLTests.group
        )


    def setUp(self):
        self.guest_client = Client() #не авторизированный клиент
        self.auth_client = Client()
        self.auth_client.force_login(StaticURLTests.user) # авторизированный клиент, но не автор поста
        self.author_client = Client()
        self.author_client.force_login(StaticURLTests.user_author) #клиент авторизированный автором поста

    def test_homepage(self):
        """Доступность главной страницы"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_group_page(self):
        """Доступность страницы с постами определенной группы"""
        response = self.guest_client.get('/group/slug-test/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_profile_page(self):
        """Доступность страницы с постами определенного пользователя"""
        response = self.guest_client.get('/profile/test_u/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
    
    def test_post_detail_page(self):
        """Доступность подробной информации о посте"""
        response = self.guest_client.get('/post/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_edit_post_page(self):
        """Доступность страницы редиктирования поста со страницы автора данного поста"""
        response = self.author_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_edit_post_page_redirect(self):
        """Редирект со страницы редоктирования поста на страницу авторизации пользователя, который не автор поста"""
        response = self.auth_client.get('/posts/1/edit/', follow = True)
        self.assertRedirects(response, '/auth/login/')

    def test_create_post_page(self):
        """Доступность создания поста для авторизированного пользователя /create/"""
        response = self.auth_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_create_post_page_redirect(self):
        """Редирект с /create/ не авторизированнного пользователя на строницу входа"""
        response = self.guest_client.get('/create/', follow = True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_urls_templates(self):
        """URL-адрес использует соответствующий шаблон"""
        urls_template_name = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/post/1/': 'posts/post_detail.html',
            '/profile/test_u/': 'posts/profile.html',
            '/group/slug-test/': 'posts/group_list.html',
        }
        for adress, template in urls_template_name.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(response, template)