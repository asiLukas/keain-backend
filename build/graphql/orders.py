import strawberry
import strawberry_django

from build.models import Build


@strawberry_django.order_type(Build)
class BuildOrder:
    name: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto
