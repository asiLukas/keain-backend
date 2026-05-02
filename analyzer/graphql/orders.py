import strawberry
import strawberry_django

from analyzer.models import Analysis


@strawberry_django.order_type(Analysis)
class AnalysisOrder:
    created_at: strawberry.auto
    updated_at: strawberry.auto
