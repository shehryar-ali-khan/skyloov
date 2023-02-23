from django.urls import path
from .views import *

urlpatterns = [
    path('product/', ProductAPIView.as_view(), name='product_search'),
    path('cart/', CartAPIView.as_view(), name='cart'),
    path('image/upload-product-image/', ProductImageUploadView.as_view(), name='product-image-upload'),
]
