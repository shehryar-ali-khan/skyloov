from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/')


class ProductModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0.0, validators=[MaxValueValidator(5), MinValueValidator(0)])
    images = models.ManyToManyField('ProductImage', related_name='products')

    def __str__(self):
        return self.name


class CartProductModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class CartModel(models.Model):
    owner = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    products = models.ManyToManyField(CartProductModel, blank=True, related_name='related_cart')
    number_of_products = models.PositiveIntegerField(default=0)
    cart_total_price = models.DecimalField(max_digits=9, default=0, decimal_places=2)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
