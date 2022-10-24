from django.shortcuts import render
from django.views.generic import CreateView # Импортируем CreateView, чтобы создать ему наследника
from django.urls import reverse_lazy # Функция reverse_lazy позволяет получить URL по параметрам функции path()
from .forms import CreationForm # Импортируем класс формы, чтобы сослаться на неё во view-классе


class SignUp(CreateView):
    form_class = CreationForm # Из какого класса взять форму
    success_url = reverse_lazy('posts:home_page')
    template_name = 'users/signup.html' # шаблон для отображения куда будет передан шаблон формы.