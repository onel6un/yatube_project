from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm): # ModelForm → UserCreationForm → CreationForm Наследуемся со специального класса создания формы регистрации
    class Meta(UserCreationForm.Meta):
        Model = User
        fields = ('first_name', 'last_name', 'username', 'email')
