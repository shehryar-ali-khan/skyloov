from django.contrib import admin
from .models import *


# admin.site.register(CustomerModel)
admin.site.register(ProductModel)
admin.site.register(CartProductModel)
admin.site.register(CartModel)
admin.site.register(ProductImage)
