from django.contrib import admin

from .models import Ingredients, FoodIngredients, Foods, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


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

    search_fields = ('title', 'content')
    list_filter = ('is_published', 'time_create')
