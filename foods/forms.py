from django import forms

from . import validators
from .models import Foods


class AddPostForm(forms.ModelForm):
    title = forms.CharField(max_length=255)
    content = forms.CharField(widget=forms.Textarea)
    photo = forms.ImageField()
    category = forms.CharField(max_length=126, validators=[validators.category_validator])
    portions = forms.IntegerField(min_value=0)
    ingredients = forms.CharField(
        widget=forms.Textarea,
        validators=[validators.ingredients_validator]
    )
    calories = forms.IntegerField(min_value=0)

    class Meta:
        model = Foods
        fields = ('title', 'content', 'photo', 'category', 'portions', 'ingredients', 'calories')
