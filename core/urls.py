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

import strawberry
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from strawberry.django.views import AsyncGraphQLView

api = NinjaAPI(title="Keain API", version="1.0.0")


@api.post("/upload-audio")
def upload_audio(request):
    return {"status": "success", "upload_url": "https://TODO"}


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "yo TODO"


schema = strawberry.Schema(query=Query)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("graphql/", AsyncGraphQLView.as_view(schema=schema)),
]
