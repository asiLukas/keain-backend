from typing import List, Optional

import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from analyzer.graphql.filters import AnalysisFilter
from analyzer.graphql.orders import AnalysisOrder
from analyzer.models import Analysis
from build.graphql.types import BuildType


@strawberry.input
class AnalyzeInput:
    file: Upload


@strawberry_django.type(Analysis, filters=AnalysisFilter, order=AnalysisOrder, pagination=True)
class AnalysisType:
    id: strawberry.auto
    build: BuildType | None
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
    verdict: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto

    @strawberry.field
    def score(self) -> float:
        return (self.thock + self.clack) / 2.0


@strawberry.type
class AnalysisStats:
    best_thock: int
    best_clack: int
    best_score: float
    # Avg score (last 7d) minus avg score (prior 7d), rounded to 1 decimal.
    week_delta: float
