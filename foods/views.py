from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views import generic

from .forms import AddPostForm
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


class AddPostView(generic.CreateView):
    form_class = AddPostForm
    success_url = reverse_lazy('home')
    template_name = "foods/add.html"

    def form_valid(self, form: AddPostForm):
        params = {"format": "{cat_name} - {amount or mass}"}

        obj = Category.objects.filter(name=form.data['category'])
        if not obj:
            raise ValidationError(
                message=_("No such category: %(cat)s"),
                code="invalid",
                params={"cat": form.data['category']}
            )

        for ing in form.data['ingredients'].split("\n"):
            print(ing)
            if ing.find('-') == -1:
                raise ValidationError(
                    message=_("Wrong format: %(format)s"),
                    code="invalid",
                    params=params
                )
            name, mass_or_count = ing.split('-')
            mass, count = None, None
            mass_or_count = mass_or_count.rstrip(" ")
            if mass_or_count.find("шт") == -1:
                if mass_or_count.find("г") == -1:
                    raise ValidationError(
                        message=_("Wrong format: %(format)s"),
                        code="invalid",
                        params=params
                    )
                else:
                    mass, x = mass_or_count.split()
            else:
                count, x = mass_or_count.split()

            ing = FoodIngredients(food=form.instance)
            if mass:
                ing.mass = int(mass)
            else:
                ing.amount = int(count)

            parent_ingred = Ingredients.objects.filter(name=name)

            if not parent_ingred:
                raise ValidationError(
                    message=_("Parent ingredient was not found: %(ing)s"),
                    code="invalid",
                    params={"ing": name},
                )
            ing.ingredient = parent_ingred
            ing.save()
        form.save()

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
