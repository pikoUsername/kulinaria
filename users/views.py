from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views import generic

from users.forms import LoginForm, SignUpForm

User = get_user_model()


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = "registration/signup.html"


class LoginView(DjangoLoginView):
    form_class = LoginForm
