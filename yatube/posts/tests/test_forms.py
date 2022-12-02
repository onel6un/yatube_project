import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from ..models import Post, Group, Comment
from ..forms import PostForm
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django import forms
from django.conf import settings

User = get_user_model()

class PostFormTest(TestCase):

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
            author = PostFormTest.user_author,
            group = PostFormTest.group
        )


    def setUp(self):
        self.guest_client = Client() #не авторизированный клиент
        self.auth_client = Client()
        self.auth_client.force_login(PostFormTest.user) # авторизированный клиент, но не автор поста
        self.author_client = Client()
        self.author_client.force_login(PostFormTest.user_author) #клиент авторизированный автором поста

    def test_create_post(self):
        count_post = Post.objects.count()
        form_data = {
            'text': 'Текст формы'
        }
        self.auth_client.post(reverse('posts:create'), form_data, follow=True)
        self.assertEqual(count_post +1, Post.objects.count()) # проверяем что добавился еще один пост после отправки формы
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists()) # проверяем, что в базу добавлена запись с данными переданными напи в пост запросе

    def test_edit_post(self):
        change_data = {
            'text': 'Измененный текст'
        }
        # отправляем пост запрос с заполнеными полями формы chage_data на страницу редактирования поста
        self.author_client.post(reverse('posts:edit', kwargs={'post_id': '1'}), change_data, follow=True)
        # проверяем что измененный пост есть в базе данных. 
        self.assertTrue(Post.objects.filter(text=change_data['text']).exists())



# Создаем временную папку для медиа-файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImgPostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_u')  # 'Просто авторизированный пользователь'
        cls.user_author = User.objects.create(username='test_a')  # юзер - автор тестогово поста
        cls.group = Group.objects.create(
            title = 'Тестовый заголовок группы',
            slug = 'slug-test',
            description = 'Тестовое описание'
        )
        

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


    def setUp(self):
        self.guest_client = Client()  # не авторизированный клиент
        self.auth_client = Client()
        self.auth_client.force_login(ImgPostTest.user)  # авторизированный клиент, но не автор поста

    def test_create_post(self):
        '''проверяет. что при отправке поста с картинкой через форму PostForm создаётся запись в базе данных.'''
        post_count = Post.objects.count()
        small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'image': uploaded,
            'group': '1',
        }
        response = self.auth_client.post(
            reverse('posts:create'),
            form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count+1)
        
        #  проверим передачу изображения в context 
        context = {
            reverse('posts:home_page'): 'posts/small.gif',
            (reverse('posts:profile', kwargs={'username': 'test_u'})): 'posts/small.gif',
            (reverse('posts:group_list', kwargs={'slug': 'slug-test'})): 'posts/small.gif',
        }

        for url, img in context.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.context['page_obj'][0].image.name, img)


class CommentFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_u') #'Просто авторизированный пользователь'
        cls.user_author = User.objects.create(username = 'test_a') # юзер - автор тестогово поста
        cls.post = Post.objects.create(
            text = 'Тестовый текст',
            author = CommentFormTest.user_author,
        )


    def setUp(self):
        self.guest_client = Client() #не авторизированный клиент
        self.auth_client = Client()
        self.auth_client.force_login(CommentFormTest.user) # авторизированный клиент, но не автор поста
        self.author_client = Client()
        self.author_client.force_login(CommentFormTest.user_author) #клиент авторизированный автором поста


    def test_comment_form(self):
        '''Проверка добавления коммпентария'''
        count_comment = Comment.objects.count()
        form_data = {
            'text': 'тестовый коммент'
        }
        self.auth_client.post(reverse('posts:add_comment', kwargs={'post_id': '1'}), form_data, follow=True)
        #  после отправки формы количество комментариев увеличилось
        self.assertEqual(count_comment+1, Comment.objects.count())
        count_comment = Comment.objects.count()
        #  проверим отправку комментария не зарегестрированным пользователем
        self.guest_client.post(reverse('posts:add_comment', kwargs={'post_id': '1'}), form_data, follow=True)
        self.assertEqual(count_comment, Comment.objects.count())