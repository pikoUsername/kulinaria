from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect

from .models import *


def index(request):
    posts = Foods.objects.all()
    cats = Category.objects.all()
    context = {
        'posts': posts,
        'cats': cats,
        'title': 'Главная страница',
        'cat_selected': 0,
    }
    return render(request, 'foods/index.html', context=context)

def about(request):
    return render(request, 'foods/about.html',  {'title': 'О сайте'})

def addpage(request):
    return HttpResponse("Добавление статьи")

def contact(request):
    return HttpResponse("Обратная связь")

def show_post(request, post_id):
    return HttpResponse(f"Отображение статьи с id= {post_id}")

def showcategory(request, cat_id):
    return HttpResponse(f"Отображение категории с id= {cat_id}")

def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
