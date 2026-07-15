from django.urls import path
from DjangoEcommerceApp import FrontEndViews

urlpatterns = [
    path('', FrontEndViews.home_page, name="home_page"),
    path('product/<int:product_id>/<str:product_slug>/', FrontEndViews.product_details, name="product_details"),
    path('category/<str:category_slug>/', FrontEndViews.category_product_list, name="category_product_list"),
    path('cart/', FrontEndViews.cart_view, name="cart_view"),
    path('update_cart/<int:product_id>/<str:action>/', FrontEndViews.update_cart, name="update_cart"),
    path('add_to_cart/<int:product_id>/', FrontEndViews.add_to_cart, name="add_to_cart"),
    path('signup/', FrontEndViews.signup, name="signup"),
    path('profile/', FrontEndViews.profile_view, name="profile_view"),
]
