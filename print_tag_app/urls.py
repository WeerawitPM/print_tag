from django.urls import path
from print_tag_app import views

# from .views import get_modal_data

urlpatterns = [
    path("", views.index),
    path("invoice/<str:fcskid>/", views.get_invoice_data, name="get_invoice_data"),
    path("autocomplete", views.autocomplete, name="autocomplete"),
    path("save_selected", views.save_selected, name="save_selected"),
    # path('get_modal_data/<str:fcskid>/', get_modal_data, name='get_modal_data'),
    path("upload_packing/", views.upload_packing, name="upload_packing"),
    path("product", views.product, name="product"),
    path("save_product", views.save_product, name="save_product"),
]
