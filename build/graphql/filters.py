import strawberry
import strawberry_django

from build.models import Build


@strawberry_django.filter_type(Build, lookups=True)
class BuildFilter:
    name: strawberry.auto
    case: strawberry.auto
    plate: strawberry.auto
    pcb: strawberry.auto
    keycap_set: strawberry.auto
    stabilizer: strawberry.auto
    switch: strawberry.auto
