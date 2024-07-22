from django.urls import path
from print_tag_app import views

urlpatterns = [
    path("", views.index),
    path('autocomplete', views.autocomplete, name='autocomplete'),
    path('save_selected', views.save_selected, name='save_selected'),
]