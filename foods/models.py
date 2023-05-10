from django.db import models
from django.urls import reverse


class TimedModel(models.Model):
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimedModel):
    name = models.CharField(max_length=100, db_index=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Categorie"

    def __str__(self):
        return self.name


class Ingredients(TimedModel):
    # you can access food_ingredients through obj.food_ingredients_set
    name = models.CharField(null=False, max_length=128, primary_key=True)
    price = models.PositiveIntegerField(null=False)
    calories = models.PositiveIntegerField(null=True)

    class Meta:
        db_table = "ingredients"
        verbose_name = "Ingredient"

    def __str__(self):
        return self.name


class Foods(TimedModel):
    # you can use foods.ingredients_set
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    call = models.TextField(blank=True)
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/")

    is_published = models.BooleanField(default=True)
    cat = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)

    portions = models.PositiveSmallIntegerField(verbose_name="Порции", null=True)
    calories = models.PositiveIntegerField(null=True)

    class Meta:
        db_table = "foods"
        ordering = ["title"]
        verbose_name = "Food"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # to post
        return reverse('post', kwargs={'post_id': self.pk})

    def get_absoluted_url(self):
        return reverse('category', kwargs={'cat_id': self.pk})


class FoodIngredients(TimedModel):
    # in gramms
    mass = models.PositiveIntegerField(null=False)
    amount = models.PositiveIntegerField(null=False)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    food = models.ForeignKey(Foods, on_delete=models.CASCADE)

    class Meta:
        db_table = "food_ingredients"
        verbose_name = "FoodIngredient"

    def __str__(self):
        return self.ingredient.__str__()
