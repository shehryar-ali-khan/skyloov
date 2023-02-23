from rest_framework import serializers
from .models import *


class ProductsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = '__all__'


SORTING_FIELD = ("category", "brand", "price", "quantity", "rating")


class ProductsGetSerializer(serializers.Serializer):
    category = serializers.CharField(max_length=255, required=False)
    brand = serializers.CharField(max_length=255, required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=9, decimal_places=2, required=False)
    min_quantity = serializers.IntegerField(required=False)
    max_quantity = serializers.IntegerField(required=False)
    rating = serializers.FloatField(required=False)  # TODO rating greater in search
    created_at = serializers.DateTimeField(required=False)
    sorting_param = serializers.ChoiceField(required=False, choices=SORTING_FIELD, default="category")
    item_per_page = serializers.IntegerField(required=False,default=5)
    page = serializers.IntegerField(required=False,default=1)


class ProductPostSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    category = serializers.CharField(max_length=255)
    brand = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=9, decimal_places=2)
    quantity = serializers.IntegerField()
    is_active = serializers.BooleanField(default=True)
    rating = serializers.FloatField(default=0.0)

    def create(self, validated_data):
        return ProductModel.objects.create(**validated_data)


class CartProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    qty = serializers.IntegerField(required=True)
    final_price = serializers.FloatField(required=True)


class CartSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=True)
    products = CartProductSerializer(required=True, many=True)
    number_of_products = serializers.IntegerField(required=True)
    cart_total_price = serializers.FloatField(required=True)


class SpecificCartSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class CartProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProductModel
        fields = ['product','qty','final_price']


class CartDetailSerializer(serializers.ModelSerializer):
    products = CartProductDetailSerializer(many=True)

    class Meta:
        model = CartModel
        fields = ['products','number_of_products','cart_total_price']


class ProductImageSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    image = serializers.ImageField(required=True)
