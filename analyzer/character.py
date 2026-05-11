from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from analyzer.models import MetricChoice, is_inverted

_PROFILE: Dict[MetricChoice, Dict[str, Sequence[Sequence[str]]]] = {
    MetricChoice.THOCK: {
        "adj": (
            ("Hollow", "Tin", "Empty"),
            ("Round", "Mellow", "Plump"),
            ("Cavernous", "Subterranean", "Abyssal"),
        ),
        "noun": ("Thock", "Thump", "Drum"),
    },
    MetricChoice.CLACK: {
        "adj": (
            ("Padded", "Cushioned", "Muffled"),
            ("Crisp", "Snappy", "Brisk"),
            ("Glassy", "Razor", "Cutting"),
        ),
        "noun": ("Clack", "Snap", "Crack"),
    },
    MetricChoice.CREAMINESS: {
        "adj": (
            ("Brittle", "Parched", "Husked"),
            ("Velvet", "Silken", "Smooth"),
            ("Buttery", "Silky", "Marshmallow"),
        ),
        "noun": ("Cream", "Body", "Loaf"),
    },
    MetricChoice.PURITY: {
        "adj": (
            ("Sandy", "Grinding", "Chalky"),
            ("Polished", "Refined", "Filtered"),
            ("Crystalline", "Pristine", "Diamond"),
        ),
        "noun": ("Signal", "Tone", "Note"),
    },
    MetricChoice.CONSISTENCY: {
        "adj": (
            ("Drifting", "Wobbly", "Scattered"),
            ("Grounded", "Steady", "Even"),
            ("Surgical", "Locked", "Precision"),
        ),
        "noun": ("Strike", "Profile", "Rhythm"),
    },
    MetricChoice.TONAL_BALANCE: {
        "adj": (
            ("Glassy", "Icy", "Brilliant"),
            ("Balanced", "Centered", "Even"),
            ("Honeyed", "Mellow", "Toasted"),
        ),
        "noun": ("Voice", "Timbre", "Hue"),
    },
    MetricChoice.PITCH: {
        "adj": (
            ("Soprano", "Treble", "Chime"),
            ("Tenor", "Mid", "Hollow"),
            ("Bass", "Subwoofer", "Cavern"),
        ),
        "noun": ("Register", "Pitch", "Voicing"),
    },
}

_CHARACTER_METRICS: Tuple[MetricChoice, ...] = tuple(_PROFILE.keys())

_SECONDARY_MIN_DISTANCE = 15


def _norm(scores: Mapping[MetricChoice, int], metric: MetricChoice) -> int:
    raw = int(scores[metric])
    return 100 - raw if is_inverted(metric) else raw


def _tier(norm: int) -> int:
    if norm < 35:
        return 0
    if norm >= 65:
        return 2
    return 1


def _js_pick(items: Sequence[str], seed: str) -> str:
    h = 0
    for ch in seed:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return items[abs(h) % len(items)]


def compute_character_title(scores: Mapping[MetricChoice, int]) -> str:
    ranked: List[Tuple[MetricChoice, int, int]] = []
    for m in _CHARACTER_METRICS:
        n = _norm(scores, m)
        ranked.append((m, n, abs(n - 50)))
    ranked.sort(key=lambda r: r[2], reverse=True)

    top_metric, top_norm, _ = ranked[0]
    second_metric, second_norm, second_dist = ranked[1]

    use_second = second_dist >= _SECONDARY_MIN_DISTANCE and second_metric != top_metric
    if use_second:
        adj_metric, adj_norm = second_metric, second_norm
    else:
        adj_metric, adj_norm = top_metric, top_norm

    top_profile = _PROFILE[top_metric]
    adj_profile = _PROFILE[adj_metric]

    seed = f"{top_metric.value}{adj_metric.value}{top_norm}{adj_norm}"
    adj = _js_pick(adj_profile["adj"][_tier(adj_norm)], f"{seed}a")
    noun = _js_pick(top_profile["noun"], f"{seed}n")
    return f"{adj} {noun}"
