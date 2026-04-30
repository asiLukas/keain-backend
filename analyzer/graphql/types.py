from typing import List, Optional

import strawberry
from strawberry.file_uploads import Upload


@strawberry.input
class AnalyzeInput:
    file: Upload


@strawberry.type
class AnalyzeResult:
    message: str
    thock: int
    clack: int
    creaminess: int
    pitch: int
    consistency: int
    tonal_balance: int
    peak_resonance: int
    purity: int
    peak_loudness: int
    metallic_resonance: int
    variance: int
    frequency_response: List[float]
    verdict: Optional[str]  # behind paywall, TODO
