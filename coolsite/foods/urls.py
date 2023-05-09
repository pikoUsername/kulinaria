from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('about/', about, name='about'),
    path('add/', addpage, name='add_page'),
    path('contact/', contact, name='contact'),
    path('login/', login, name='login'),
    path('post/<int:post_id>/', show_post, name='post'),
    path('category/<int:cat_id>/', showcategory, name='category'),
]