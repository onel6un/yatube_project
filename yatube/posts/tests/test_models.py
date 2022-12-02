from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Post, Group

User = get_user_model()

class TestPostModels(TestCase):
    """Тестируем модели приложения Posts"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title = 'Тестовый заголовок группы',
            slug = 'Тестовый слаг',
            description = 'Тестовое описание'
        )
        cls.post = Post.objects.create(
            author = cls.user,
            text = 'Тестовый текст, ochen dlinniy, bolshe 15 simbol...'
        )
    
    def test_object_name_is_text_in_Posts(self):
        """Проверка object_name == post.text[:15]"""
        post = TestPostModels.post
        exepted_name = post.text[:15]
        self.assertEqual(str(post), exepted_name, 'object_name не свовпадает с 15 символами из текста')

    def test_object_name_is_title_in_Group(self):
        """Проверка object_name == group.title"""
        group = TestPostModels.group
        exepted_name = group.title
        self.assertEqual(str(group), exepted_name, 'object_name не свовпадает с 15 символами из заголовка')

    def test_verbose_name_in_group(self):
        ''' Проверка атрибутов verboses_name у полей модели Group'''
        group = TestPostModels.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'URL адресс',
            'description': 'Описание' 
        }
        for field, ex_verb in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(group._meta.get_field(field).verbose_name, ex_verb)

    def test_help_text_in_post(self):
        ''' Проверка атрибутов help_text у полей модели Post'''
        post = TestPostModels.post
        field_verboses = {
            'text': 'Введите текст',
            'group': 'Выберите группу', 
        }
        for field, ex_verb in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).help_text, ex_verb)