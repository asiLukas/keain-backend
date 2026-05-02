import strawberry
import strawberry_django

from analyzer.models import Analysis


@strawberry_django.filter_type(Analysis, lookups=True)
class AnalysisFilter:
    build: strawberry.auto
    created_at: strawberry.auto
