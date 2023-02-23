import os
import threading
import traceback
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from drf_yasg import openapi
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from PIL import Image
from io import BytesIO
from rest_framework_simplejwt.authentication import JWTAuthentication


def generate_thumbnail(image_file):
    thumbnail_size = (200, 200)

    with Image.open(image_file) as img:
        img.thumbnail(thumbnail_size)
        thumb_io = BytesIO()
        img.save(thumb_io, img.format)
        thumbnail_file = thumb_io.getvalue()

    return thumbnail_file


def generate_full_size_image(image_file):
    full_size = (800, 800)

    with Image.open(image_file) as img:
        img.thumbnail(full_size)
        full_size_io = BytesIO()
        img.save(full_size_io, img.format)
        full_size_file = full_size_io.getvalue()

    return full_size_file


class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        query_serializer=ProductsGetSerializer)
    def get(self, request):
        serializer = ProductsGetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = None
        try:
            products = ProductModel.objects.all().order_by(serializer.validated_data['sorting_param'])
            if serializer.validated_data.get('category'):
                products = products.filter(category=serializer.validated_data['category'])
            if serializer.validated_data.get('brand'):
                products = products.filter(brand=serializer.validated_data['brand'])
            if serializer.validated_data.get('min_price'):
                products = products.filter(price__gte=serializer.validated_data['min_price'])
            if serializer.validated_data.get('max_price'):
                products = products.filter(price__lte=serializer.validated_data['max_price'])
            if serializer.validated_data.get('min_quantity'):
                products = products.filter(quantity__gte=serializer.validated_data['min_quantity'])
            if serializer.validated_data.get('max_quantity'):
                products = products.filter(quantity__lte=serializer.validated_data['max_quantity'])
            if serializer.validated_data.get('rating'):
                products = products.filter(rating__gte=serializer.validated_data['rating'])
            if serializer.validated_data.get('created_at'):
                products = products.filter(created_at=serializer.validated_data['created_at'])
            if serializer.validated_data.get('page'):
                page = serializer.validated_data['page']
            if serializer.validated_data.get('item_per_page'):
                item_per_page = serializer.validated_data['item_per_page']
                serializer = ProductsDetailSerializer(products, many=True).data
                paginator = Paginator(serializer, item_per_page)  # Show 25 products per page
                data = paginator.get_page(page).object_list
        except Exception as exception:
            print(str(traceback.format_exc()))  # TODO use logger.error
        return Response(data, status=status.HTTP_200_OK)

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ProductPostSerializer)
    def post(self, request):
        serializer = ProductPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if serializer.is_valid():
                serializer.create(serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exception:
            print(str(traceback.format_exc()))  # TODO use logger.error
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(query_serializer=SpecificCartSerializer)
    def get(self, request):
        serializer = SpecificCartSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        try:
            if not CartModel.objects.filter(id=serializer.validated_data['id'], is_valid=True).exists():
                raise Http404
            cartObj = CartModel.objects.get(id=serializer.validated_data['id'], is_valid=True)
            cartObj = CartDetailSerializer(cartObj)
            return Response(cartObj.data, status=status.HTTP_200_OK)
        except Exception as exception:
            print(str(traceback.format_exc()))  # TODO use logger.error
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=CartSerializer)
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if serializer.is_valid():
                customerObj = User.objects.get(id=serializer.validated_data['customer_id'])
                cartProductList = []
                for dataItems in serializer.validated_data['products']:
                    productObj = ProductModel.objects.get(id=dataItems['product_id'])
                    cartProductObj = CartProductModel.objects.create(product=productObj, qty=dataItems['qty'],
                                                                     final_price=dataItems['final_price'])
                    cartProductList.append(cartProductObj)
                cartObj = CartModel.objects.create(number_of_products=serializer.validated_data['number_of_products'],
                                                   cart_total_price=serializer.validated_data['cart_total_price'])
                cartObj.owner = customerObj
                cartObj.products.add(*cartProductList)
                cartObj.save()

        except Exception as exception:
            print(str(traceback.format_exc()))  # TODO use logger.error
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductImageUploadView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=ProductImageSerializer)
    def post(self, request):
        serializer = ProductImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if serializer.is_valid():
                productObj = ProductModel.objects.get(id=serializer.validated_data['product_id'])
                image_file = serializer.validated_data['image']

            if image_file:
                product_image = ProductImage.objects.create(image=image_file)
                productObj.images.add(product_image)
                productObj.save()

                # start image processing in a separate thread
                threading.Thread(target=process_product_image, args=(product_image.id,)).start()

                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No image provided'})
        except Exception as exception:
            print(str(traceback.format_exc()))  # TODO use logger.error
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response({}, status=status.HTTP_201_CREATED)


def process_product_image(product_image_id):
    product_image = ProductImage.objects.get(id=product_image_id)
    image_file = product_image.image.file

    thumbnail_file = generate_thumbnail(image_file)
    full_size_file = generate_full_size_image(image_file)

    # save thumbnail and full-size images to disk
    product_image.thumbnail.save(
        os.path.basename(image_file.name),
        thumbnail_file,
        save=True
    )
    product_image.full_size_image.save(
        os.path.basename(image_file.name),
        full_size_file,
        save=True
    )

    product_image.save()
