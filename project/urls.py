from django.contrib import admin
from django.urls import path, include
# from rest_framework_swagger.views import get_swagger_view
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="skyloov API",
        default_version='v1',
        description="Development",
        terms_of_service="",
        contact=openapi.Contact(email="a@b.com"),
        license=openapi.License(name="publicly not allowed"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework.urls')),
    path('api/jwtauth/', include('jwtauth.urls'), name='jwtauth'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='skyloov'),
    path('api/', include('product.urls'), name='product'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
