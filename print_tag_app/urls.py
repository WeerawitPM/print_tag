from django.urls import path
from print_tag_app import views
from .views import get_modal_data

urlpatterns = [
    path("", views.index),
    path('autocomplete', views.autocomplete, name='autocomplete'),
    path('save_selected', views.save_selected, name='save_selected'),
    path('get_modal_data/<str:fcskid>/', get_modal_data, name='get_modal_data'),
]