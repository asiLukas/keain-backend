from datetime import timedelta
from typing import List

import strawberry
import strawberry_django
from django.db.models import Avg, ExpressionWrapper, F, FloatField, Max, Min, Value
from django.utils import timezone
from graphql import GraphQLError
from strawberry import Info
from strawberry.types.info import Info
from strawberry_django.pagination import OffsetPaginated

from analyzer.graphql.filters import AnalysisFilter
from analyzer.graphql.orders import AnalysisOrder
from analyzer.graphql.types import AnalysisStats, AnalysisType, MetricBest
from analyzer.models import Analysis, MetricChoice, is_inverted
from analyzer.services import topn_for_metric
from core.permissions import IsAuthenticated
from core.utils import get_user_from_info


def metric_higher_better_expr(metric: MetricChoice) -> ExpressionWrapper:
    """Return expression normalized so higher = better (inverts low-is-better metrics)."""
    field = F(metric.lower())
    expr = (Value(100) - field) if is_inverted(metric) else field
    return ExpressionWrapper(expr, output_field=FloatField())


def get_score_for_analyzer(primary: MetricChoice, secondary: MetricChoice) -> ExpressionWrapper:
    return ExpressionWrapper(
        (metric_higher_better_expr(primary) + metric_higher_better_expr(secondary)) / 2.0,
        output_field=FloatField(),
    )


def best_agg_for(metric: MetricChoice):
    """Aggregate that picks raw best value per metric (Min if inverted, else Max)."""
    field = metric.lower()
    return Min(field) if is_inverted(metric) else Max(field)


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
        per_metric_agg = qs.aggregate(
            **{f"best_{m.lower()}": best_agg_for(m) for m in MetricChoice}
        )
        best_per_metric = [
            MetricBest(metric=m, value=per_metric_agg[f"best_{m.lower()}"] or 0.0)
            for m in MetricChoice
        ]
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
            best_primary=per_metric_agg[f"best_{primary.lower()}"] or 0,
            best_secondary=per_metric_agg[f"best_{secondary.lower()}"] or 0,
            best_score=best_score,
            week_delta=week_delta,
            best_per_metric=best_per_metric,
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    def analysis_rank_message(self, info: Info, analysis_id: strawberry.ID) -> str | None:
        user = get_user_from_info(info)
        try:
            analysis = Analysis.objects.visible_to(user).get(id=analysis_id)
        except Analysis.DoesNotExist:
            raise GraphQLError("Analysis doesn't exist")

        scores = {m: getattr(analysis, m.lower()) for m in MetricChoice}
        metric = user.primary_metric
        raw = scores[metric]
        value = (100 - raw) if is_inverted(metric) else raw

        label = topn_for_metric(
            Analysis.objects.exclude(pk=analysis.pk),
            metric,
            value,
        )
        if label is None:
            return None
        return f"{label} · {metric}"
