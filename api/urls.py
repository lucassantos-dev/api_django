from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Api Dashboard Protocolos Tax",
        default_version='v1',
        description="",
        terms_of_service="https://www.suaapi.com/terms/",
        contact=openapi.Contact(email="contato@suaapi.com"),
        license=openapi.License(name="Licença da sua API"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("djoser.urls")),
    path("api/", include("users.urls")),
    path("protocols/", include("protocols.urls")),
    # Rota para a documentação do Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # Rota para a documentação do Redoc (alternativa ao Swagger UI)
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
