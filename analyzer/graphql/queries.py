from datetime import timedelta
from typing import List

import strawberry
import strawberry_django
from django.db.models import Avg, ExpressionWrapper, F, FloatField, Max
from django.utils import timezone
from strawberry import Info
from strawberry.types.info import Info
from strawberry_django.pagination import OffsetPaginated

from analyzer.graphql.filters import AnalysisFilter
from analyzer.graphql.orders import AnalysisOrder
from analyzer.graphql.types import AnalysisStats, AnalysisType
from analyzer.models import Analysis, MetricChoice
from core.permissions import IsAuthenticated
from core.utils import get_user_from_info


def get_score_for_analyzer(primary: MetricChoice, secondary: MetricChoice) -> ExpressionWrapper:
    return ExpressionWrapper(
        (F(primary.lower()) + F(secondary.lower())) / 2.0, output_field=FloatField()
    )


@strawberry.type
class AnalyzerQuery:
    @strawberry_django.offset_paginated(
        OffsetPaginated[AnalysisType],
        filters=AnalysisFilter,
        order=AnalysisOrder,
        permission_classes=[IsAuthenticated],
    )
    def analyses(self, info: Info) -> List[AnalysisType]:
        return Analysis.objects.visible_to(get_user_from_info(info))

    @strawberry.field(permission_classes=[IsAuthenticated])
    def analysis_stats(self, info: Info) -> AnalysisStats:
        user = get_user_from_info(info)
        primary = MetricChoice(user.primary_metric)
        secondary = MetricChoice(user.secondary_metric)
        qs = Analysis.objects.visible_to(user)
        agg = qs.aggregate(
            best_primary=Max(primary.lower()),
            best_secondary=Max(secondary.lower()),
        )
        score_expr = get_score_for_analyzer(primary, secondary)
        best_score = qs.annotate(_score=score_expr).aggregate(m=Max("_score"))["m"] or 0.0

        now = timezone.now()
        last_week = qs.filter(created_at__gte=now - timedelta(days=7))
        prior_week = qs.filter(
            created_at__gte=now - timedelta(days=14),
            created_at__lt=now - timedelta(days=7),
        )
        last_avg = last_week.annotate(_score=score_expr).aggregate(a=Avg("_score"))["a"] or 0.0
        prior_avg = prior_week.annotate(_score=score_expr).aggregate(a=Avg("_score"))["a"] or 0.0
        week_delta = round((last_avg - prior_avg) * 10) / 10

        return AnalysisStats(
            best_primary=agg["best_primary"] or 0,
            best_secondary=agg["best_secondary"] or 0,
            best_score=best_score,
            week_delta=week_delta,
        )
