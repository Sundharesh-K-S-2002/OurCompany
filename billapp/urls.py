from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_page, name='register'),
    path('login/', login, name='login'),
    path('home/', home, name='home'),
    path('add_product/', add_product, name='add_product'),
    path('orders/', order, name='order'),   
    path('cart/', calculate_total, name='calculate_total'),
    path('payment/', payment, name='payment'),
    path('razorpay/', razorpay_payment, name='razorpay_payment'),
    path('success/', success, name='success'),
    path('create-order/', create_order, name='create_order'),
    path('error/', error, name='error'),
]