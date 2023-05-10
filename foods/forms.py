from django import forms

from .models import Foods


class AddPostForm(forms.ModelForm):
    title = forms.CharField(max_length=255)
    content = forms.CharField(widget=forms.Textarea)
    photo = forms.ImageField()
    category = forms.CharField(max_length=126)
    portions = forms.IntegerField(min_value=0)
    ingredients = forms.CharField(
        widget=forms.Textarea
    )
    calories = forms.IntegerField(min_value=0)

    class Meta:
        model = Foods
        fields = ('title', 'content', 'photo', 'category', 'portions', 'ingredients', 'calories')
