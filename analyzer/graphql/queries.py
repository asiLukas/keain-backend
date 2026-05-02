from datetime import timedelta
from typing import List, Optional

import strawberry
import strawberry_django
from django.db.models import Avg, ExpressionWrapper, F, FloatField, Max
from django.utils import timezone
from strawberry.types.info import Info
from strawberry_django.pagination import OffsetPaginated

from analyzer.graphql.filters import AnalysisFilter
from analyzer.graphql.orders import AnalysisOrder
from analyzer.graphql.types import AnalysisStats, AnalysisType
from analyzer.models import Analysis
from core.permissions import IsAuthenticated


# TODO move to project wide utils, or create some decorator idk
def _user(info: Info):
    return info.context.get("user")


def _score_expr() -> ExpressionWrapper:
    return ExpressionWrapper((F("thock") + F("clack")) / 2.0, output_field=FloatField())


@strawberry.type
class AnalyzerQuery:
    @strawberry_django.offset_paginated(
        OffsetPaginated[AnalysisType],
        filters=AnalysisFilter,
        order=AnalysisOrder,
        permission_classes=[IsAuthenticated],
    )
    def analyses(self, info: Info) -> List[AnalysisType]:
        return Analysis.objects.visible_to(_user(info))

    @strawberry.field(permission_classes=[IsAuthenticated])
    def analysis_stats(self, info: Info) -> AnalysisStats:
        qs = Analysis.objects.visible_to(_user(info))
        agg = qs.aggregate(best_thock=Max("thock"), best_clack=Max("clack"))
        best_score = qs.annotate(_score=_score_expr()).aggregate(m=Max("_score"))["m"] or 0.0

        now = timezone.now()
        last_week = qs.filter(created_at__gte=now - timedelta(days=7))
        prior_week = qs.filter(
            created_at__gte=now - timedelta(days=14),
            created_at__lt=now - timedelta(days=7),
        )
        last_avg = last_week.annotate(_score=_score_expr()).aggregate(a=Avg("_score"))["a"] or 0.0
        prior_avg = prior_week.annotate(_score=_score_expr()).aggregate(a=Avg("_score"))["a"] or 0.0
        week_delta = round((last_avg - prior_avg) * 10) / 10

        return AnalysisStats(
            best_thock=agg["best_thock"] or 0,
            best_clack=agg["best_clack"] or 0,
            best_score=best_score,
            week_delta=week_delta,
        )
