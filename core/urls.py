"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from typing import Any, Dict

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from strawberry.django.views import GraphQLView

from .schema import schema


class KeainGraphQLView(GraphQLView):
    def get_context(self, request, response) -> Dict[str, Any]:  # type: ignore[override]
        from user.graphql.utils import get_user_from_request

        return {"request": request, "response": response, "user": get_user_from_request(request)}


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "graphql/",
        csrf_exempt(KeainGraphQLView.as_view(schema=schema, multipart_uploads_enabled=True)),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
