from django.db import models
from django.urls import reverse


class TimedModel(models.Model):
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimedModel):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class Ingredients(TimedModel):
    # you can access food_ingredients through obj.food_ingredients_set
    name = models.CharField(null=False, max_length=128)
    price = models.PositiveIntegerField(null=False)
    calories = models.PositiveIntegerField(null=True)



class Foods(TimedModel):
    # you can use foods.ingredients_set
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    call = models.TextField(blank=True)
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/")

    is_published = models.BooleanField(default=True)
    cat = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]

    def get_absolute_url(self):
        # to post
        return reverse('post', kwargs={'post_id': self.pk})

    def get_absoluted_url(self):
        return reverse('category', kwargs={'cat_id': self.pk})


class FoodIngredients(TimedModel):
    # in gramms
    mass = models.PositiveIntegerField(null=False)
    ingredient = models.OneToOneField(Ingredients, on_delete=models.CASCADE)
    food = models.ForeignKey(Foods, on_delete=models.CASCADE)
