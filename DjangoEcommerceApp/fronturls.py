from django.urls import path
from DjangoEcommerceApp import FrontEndViews

urlpatterns = [
    path('', FrontEndViews.home_page, name="home_page"),
    path('product/<str:product_slug>/', FrontEndViews.product_details, name="product_details"),
    path('add_to_cart/<int:product_id>/', FrontEndViews.add_to_cart, name="add_to_cart"),
]
