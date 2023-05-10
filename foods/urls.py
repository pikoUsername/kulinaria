from django.urls import path
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('about/', about, name='about'),
    path('add/', AddPostView.as_view(), name='add_page'),
    path('contact/', TemplateView.as_view(template_name="contact.html"), name='contact'),
    path('post/<int:post_id>/', show_post, name='post'),
    path('category/<int:cat_id>/', showcategory, name='category'),
]
