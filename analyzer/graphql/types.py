from typing import TYPE_CHECKING, Annotated, List, Optional

import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from analyzer.graphql.filters import AnalysisFilter
from analyzer.graphql.orders import AnalysisOrder
from analyzer.models import Analysis, MetricChoice

if TYPE_CHECKING:
    from build.graphql.types import BuildType


@strawberry.input
class AnalyzeInput:
    file: Upload


@strawberry_django.type(Analysis, filters=AnalysisFilter, order=AnalysisOrder, pagination=True)
class AnalysisType:
    id: strawberry.auto
    build: Annotated["BuildType", strawberry.lazy("build.graphql.types")] | None
    audio: strawberry.auto
    message: strawberry.auto
    thock: strawberry.auto
    clack: strawberry.auto
    creaminess: strawberry.auto
    pitch: strawberry.auto
    consistency: strawberry.auto
    tonal_balance: strawberry.auto
    peak_resonance: strawberry.auto
    purity: strawberry.auto
    peak_loudness: strawberry.auto
    metallic_resonance: strawberry.auto
    variance: strawberry.auto
    frequency_response: Optional[List[float]]
    frequency_response_hz: Optional[List[float]]
    peak_hz: strawberry.auto
    tonal_note: strawberry.auto
    tonal_hz: strawberry.auto
    tonal_cents: strawberry.auto
    tonal_range: strawberry.auto
    character_title: strawberry.auto
    verdict: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto

    @strawberry.field
    def score(self) -> float:
        return (self.thock + self.clack) / 2.0


@strawberry.type
class MetricBest:
    metric: MetricChoice
    value: float


@strawberry.type
class AnalysisStats:
    best_primary: int
    best_secondary: int
    best_score: float
    # Avg score (last 7d) minus avg score (prior 7d), rounded to 1 decimal.
    week_delta: float
    best_per_metric: List[MetricBest]
