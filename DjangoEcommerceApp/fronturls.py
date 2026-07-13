from django.urls import path
from DjangoEcommerceApp import FrontEndViews

urlpatterns = [
    path('', FrontEndViews.home_page, name="home_page"),
]
