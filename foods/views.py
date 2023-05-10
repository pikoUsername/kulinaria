from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404

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

def showcategory(request, cat_id):
    return HttpResponse(f"Отображение категории с id= {cat_id}")


def show_post(request, post_id: int):
    food = get_object_or_404(Foods, pk=post_id)
    ingredients = FoodIngredients.objects.filter(id=food.pk)

    calories = 0
    for ing in ingredients:
        calories += ing.ingredient.calories

    context = {'food': food, 'ingredients': ingredients, 'category': food.cat, 'calories': calories}

    return render(request, 'foods/food.html', context=context)


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
