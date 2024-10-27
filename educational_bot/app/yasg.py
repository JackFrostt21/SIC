# from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator


class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="REST api",
        default_version='v1.0.2',
        description='''

Some useful links:
 - [Auth token](https://cdb.haemalogic.uz/api/token/)
        ''',
        license=openapi.License(name="BSD License"),
    ),
    public=False,
    generator_class=CustomSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)
