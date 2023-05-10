from django.contrib import admin

from .models import Ingredients, FoodIngredients, Foods, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(FoodIngredients)
class FoodIngredientsAdmin(admin.ModelAdmin):
    pass


class FoodIngredientsInline(admin.TabularInline):
    model = FoodIngredients


@admin.register(Foods)
class FoodsAdmin(admin.ModelAdmin):
    inlines = (FoodIngredientsInline,)
