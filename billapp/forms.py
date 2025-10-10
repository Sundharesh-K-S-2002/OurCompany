from django.forms import ModelForm
from .models import *


class RegistrationForm(ModelForm):
    class Meta:
        model = reg
        fields = ['username', 'password', 'email', 'number']

class productForm(ModelForm):
    class Meta:
        model = Products
        fields = ['productimage', 'productname', 'productcode', 'price', 'quantity']

