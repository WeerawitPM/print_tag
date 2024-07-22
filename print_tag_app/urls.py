from django.urls import path
from print_tag_app import views

urlpatterns = [
    path("", views.index),
    path('autocomplete', views.autocomplete, name='autocomplete'),
]