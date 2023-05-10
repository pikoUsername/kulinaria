from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Обязателен. Пропишите валидный е-мейл.')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', )


class LoginForm(AuthenticationForm):
    email = forms.CharField(max_length=256, required=True)

    class Meta:
        fields = ('username', 'email', 'password')

