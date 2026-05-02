"""Keyboard typing-test audio analysis.

Free tier uses librosa-only DSP. Premium tier (TODO) will layer ML on top.

Audio assumed to come from a mobile microphone (44.1/48 kHz, mono, possibly
m4a/aac/wav). Mobile mics roll off below ~80 Hz and apply AGC, so we
high-pass at 80 Hz and peak-normalize before feature extraction.

Frequency bands chosen for mechanical keyboard acoustics:
    - Thock      100 -   500 Hz   deep, dampened bottom-out (foam, gasket)
    - Body       500 -  2000 Hz   case + plate resonance
    - Clack     2000 -  8000 Hz   sharp top-out / keycap click (ABS, stiff)
    - Metallic  3000 -  6000 Hz   spring/leaf ping (narrow peaks; per
                                  attackshark.com ping = 2-5kHz)
"""

from __future__ import annotations

from io import BytesIO
from typing import List

import av
import librosa
import numpy as np
from graphql import GraphQLError
from scipy.signal import butter, sosfiltfilt

from core.error_codes import INVALID_AUDIO, err

from .graphql.types import AnalyzeResult

SR = 22050  # Nyquist 11025 Hz covers full audible keyboard range
MAX_DURATION_S = 10.0
HPF_CUTOFF_HZ = 80
N_FFT = 1024  # ~46ms window; better transient resolution than 2048 (93ms)
HOP = 256
N_FREQ_RESPONSE_BINS = 32
MIN_ONSET_GAP_S = 0.04  # 40ms debounce; merges key-down + key-up doubles

THOCK_BAND = (100.0, 500.0)
BODY_BAND = (500.0, 2000.0)
CLACK_BAND = (2000.0, 8000.0)
METALLIC_BAND = (3000.0, 6000.0)

# ---- Validation thresholds ----
# Calibrated for mobile-mic recordings of mechanical keyboards. Mech strokes
# naturally produce tonal decay from case resonance, so flatness/decay limits
# are loose to avoid rejecting valid recordings. Crank tighter only if false
# positives become a problem.
VALID_CLIP_FRACTION_MAX = 0.002  # >0.2% of samples saturated = real flat-top clipping
VALID_PEAK_MIN_DBFS = -50.0  # below = essentially silent (was -45, allow quiet recordings)
VALID_MIN_STROKES = 3  # need >=2 for CV; +1 for stable stats
VALID_MAX_STROKE_RATE = 15.0  # physiological max ~12/sec; tight margin
VALID_MIN_CREST = 2.0  # below = no transients (was 3.0; allow softer linears)
# Inter-stroke gap flatness: silence/noise floor between hits is broadband
# (flatness ~0.2-1.0). Music/speech bleeds in as sustained tonal content
# (flatness ~0.001-0.01). PC fans/HVAC have tonal harmonics that drop
# flatness to ~0.02-0.05 — those are common ambient and should NOT reject.
# Threshold 0.01 isolates real music/speech from typical room ambience.
VALID_MIN_GAP_FLATNESS = 0.01
GAP_MIN_DURATION_S = 0.05  # min 50ms gap to compute flatness reliably
VALID_MAX_DECAY_MS = 600.0  # was 350; allow reverberant rooms + heavy bottom-out


def _highpass(y: np.ndarray, sr: int, cutoff: float) -> np.ndarray:
    sos = butter(4, cutoff, btype="high", fs=sr, output="sos")
    return sosfiltfilt(sos, y).astype(np.float32)


def _band_energy(spec_avg: np.ndarray, freqs: np.ndarray, lo: float, hi: float) -> float:
    mask = (freqs >= lo) & (freqs < hi)
    if not mask.any():
        return 0.0
    return float(spec_avg[mask].sum())


def _to_score(value: float, vmin: float, vmax: float) -> int:
    if vmax == vmin:
        return 50
    s = (value - vmin) / (vmax - vmin) * 100.0
    return int(round(max(0.0, min(100.0, s))))


def _reject(reason_code: str, message: str) -> None:
    """Raise GraphQLError with structured INVALID_AUDIO code per backend convention."""
    raise GraphQLError(
        message,
        extensions=err(INVALID_AUDIO, reason=reason_code),
    )


def _validate_recording(
    *,
    peak_dbfs: float,
    clipped_fraction: float,
    n_strokes: int,
    stroke_rate: float,
    mean_crest: float,
    gap_flatness_median: float,
    mean_decay_ms: float,
) -> None:
    """Reject recordings unfit for scoring. Order matters: cheapest/most-likely first."""
    if clipped_fraction > VALID_CLIP_FRACTION_MAX:
        _reject("CLIPPED", "Audio is clipping. Lower mic gain or move farther from keyboard.")
    if peak_dbfs < VALID_PEAK_MIN_DBFS:
        _reject("TOO_QUIET", "Audio too quiet. Move closer to keyboard.")
    if n_strokes == 0:
        _reject("NO_STROKES", "No keystrokes detected.")
    if n_strokes < VALID_MIN_STROKES:
        _reject(
            "FEW_STROKES",
            f"Too few keystrokes (got {n_strokes}, need {VALID_MIN_STROKES}+). Type more.",
        )
    if stroke_rate > VALID_MAX_STROKE_RATE:
        _reject("RATE_HIGH", "Unrealistic typing speed. Record a normal typing test.")
    if mean_crest < VALID_MIN_CREST:
        _reject(
            "NO_TRANSIENTS",
            "Missing sharp transients. Sounds like continuous background noise.",
        )
    # gap_flatness_median = -1.0 means insufficient gaps measured; skip check.
    if 0.0 <= gap_flatness_median < VALID_MIN_GAP_FLATNESS:
        _reject(
            "TONAL_NOISE",
            "Tonal interference detected. Is music or speech in the recording?",
        )
    if mean_decay_ms > VALID_MAX_DECAY_MS:
        _reject(
            "TOO_RESONANT",
            "Excessive resonance/reverb. Move closer to keyboard or reduce room echo.",
        )


def _decode_audio(raw: bytes, sr: int, max_duration_s: float) -> np.ndarray:
    """Decode any container PyAV supports to mono float32 PCM at sr Hz.

    PyAV bundles libav in its wheel, so no system ffmpeg is required.
    """
    max_samples = int(sr * max_duration_s)
    chunks: List[np.ndarray] = []
    total = 0

    try:
        container = av.open(BytesIO(raw))
    except av.FFmpegError as e:
        raise RuntimeError(f"audio decode failed: {e}") from e

    try:
        if not container.streams.audio:
            raise RuntimeError("audio decode failed: no audio stream")
        stream = container.streams.audio[0]
        resampler = av.AudioResampler(format="flt", layout="mono", rate=sr)

        def _take(frames):
            nonlocal total
            for f in frames:
                arr = f.to_ndarray().reshape(-1).astype(np.float32, copy=False)
                if total + arr.size > max_samples:
                    arr = arr[: max_samples - total]
                if arr.size:
                    chunks.append(arr)
                    total += arr.size
                if total >= max_samples:
                    return True
            return False

        for frame in container.decode(stream):
            if _take(resampler.resample(frame)):
                break
        else:
            _take(resampler.resample(None))  # flush
    finally:
        container.close()

    if not chunks:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(chunks)


def analyze_keyboard_audio(file_obj) -> AnalyzeResult:
    raw = file_obj.read()
    if not raw:
        raise ValueError("Empty audio file")

    y = _decode_audio(raw, SR, MAX_DURATION_S)
    sr = SR

    if y.size < int(sr * 0.2):
        raise ValueError("Audio too short (need >=0.2s)")

    # Raw peak loudness BEFORE normalization (mobile AGC means this is rough)
    raw_peak = float(np.max(np.abs(y))) if y.size else 0.0
    peak_dbfs = float(librosa.amplitude_to_db(np.array([max(raw_peak, 1e-9)]))[0])
    # True digital clipping = many samples saturated (flat-top distortion),
    # not a single transient near fullscale. Mobile AGC pushes loud strokes
    # close to 0 dBFS without actually distorting.
    clipped_fraction = float(np.mean(np.abs(y) >= 0.999)) if y.size else 0.0

    # 1) High-pass to kill mobile-mic rumble + handling noise
    y = _highpass(y, sr, HPF_CUTOFF_HZ)

    # 2) Peak-normalize for shape comparison
    peak = float(np.max(np.abs(y)))
    if peak > 0:
        y = y / peak

    # 3) STFT
    stft = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)
    spec_avg = stft.mean(axis=1)

    # Band energies
    e_thock = _band_energy(spec_avg, freqs, *THOCK_BAND)
    e_body = _band_energy(spec_avg, freqs, *BODY_BAND)
    e_clack = _band_energy(spec_avg, freqs, *CLACK_BAND)
    e_metal = _band_energy(spec_avg, freqs, *METALLIC_BAND)
    e_audible = e_thock + e_body + e_clack + 1e-9

    thock_ratio = e_thock / e_audible
    clack_ratio = e_clack / e_audible
    metal_ratio = e_metal / e_audible

    # 4) Onset detection (then merge key-down + key-up doubles via 40ms gap)
    onset_frames = librosa.onset.onset_detect(
        y=y, sr=sr, hop_length=HOP, backtrack=True, delta=0.25, units="frames"
    )
    onset_samples_raw = librosa.frames_to_samples(onset_frames, hop_length=HOP)
    min_gap = int(MIN_ONSET_GAP_S * sr)
    filtered: List[int] = []
    for s in onset_samples_raw:
        if not filtered or int(s) - filtered[-1] >= min_gap:
            filtered.append(int(s))
    onset_samples = np.asarray(filtered, dtype=int)

    # 5) Spectral feature timeseries
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=N_FFT, hop_length=HOP)[0]
    flatness = librosa.feature.spectral_flatness(y=y, n_fft=N_FFT, hop_length=HOP)[0]

    centroid_mean = float(np.mean(centroid))
    flatness_mean = float(np.mean(flatness))

    # 6) Per-stroke features (max 80 ms post-onset, clipped to next onset)
    #    Captures: centroid, peak amp, decay time (peak -> -20dB), crest factor
    win = int(0.08 * sr)
    stroke_centroids: List[float] = []
    stroke_peaks: List[float] = []
    stroke_decays_ms: List[float] = []
    stroke_crests: List[float] = []
    for i, s in enumerate(onset_samples):
        next_s = int(onset_samples[i + 1]) if i + 1 < len(onset_samples) else y.size
        seg_end = min(int(s) + win, next_s)
        seg = y[int(s) : seg_end]
        if seg.size < N_FFT:
            continue
        sc = librosa.feature.spectral_centroid(y=seg, sr=sr, n_fft=N_FFT, hop_length=HOP)[0]
        stroke_centroids.append(float(np.mean(sc)))

        amp = np.abs(seg)
        pk_idx = int(np.argmax(amp))
        pk_val = float(amp[pk_idx])
        stroke_peaks.append(pk_val)

        # Decay time: peak -> 1/10 amplitude (-20 dB)
        post = amp[pk_idx:]
        threshold = pk_val * 0.1
        below = np.where(post < threshold)[0]
        decay_samples = int(below[0]) if below.size else int(post.size)
        stroke_decays_ms.append(1000.0 * decay_samples / sr)

        # Crest factor: peak / RMS (transient sharpness)
        rms = float(np.sqrt(np.mean(seg.astype(np.float64) ** 2)))
        stroke_crests.append(pk_val / (rms + 1e-9))

    if len(stroke_centroids) >= 2:
        c_mean = float(np.mean(stroke_centroids))
        c_std = float(np.std(stroke_centroids))
        cv_centroid = c_std / (c_mean + 1e-9)
    else:
        c_std = 0.0
        cv_centroid = 0.0

    if len(stroke_peaks) >= 2:
        p_mean = float(np.mean(stroke_peaks))
        p_cv = float(np.std(stroke_peaks)) / (p_mean + 1e-9)
    else:
        p_cv = 0.0

    cv = 0.5 * cv_centroid + 0.5 * p_cv  # combined consistency

    mean_decay_ms = float(np.mean(stroke_decays_ms)) if stroke_decays_ms else 0.0
    mean_crest = float(np.mean(stroke_crests)) if stroke_crests else 0.0

    # Inter-stroke gap flatness: detects sustained tonal bleed (music/speech)
    # in the silence BETWEEN strokes. Mech keyboard tonal decay sits inside
    # the 80ms stroke window, so gap content should be noise floor (high
    # flatness). Music/speech runs continuously → gap flatness drops low.
    gap_flatnesses: List[float] = []
    min_gap = int(GAP_MIN_DURATION_S * sr)
    gap_segments: List[tuple[int, int]] = []
    if onset_samples.size:
        # pre-first onset
        if int(onset_samples[0]) >= min_gap:
            gap_segments.append((0, int(onset_samples[0])))
        # between strokes (after stroke window ends, before next onset)
        for i in range(len(onset_samples) - 1):
            gap_start = min(int(onset_samples[i]) + win, int(onset_samples[i + 1]))
            gap_end = int(onset_samples[i + 1])
            if gap_end - gap_start >= min_gap:
                gap_segments.append((gap_start, gap_end))
        # post-last onset
        gap_start = int(onset_samples[-1]) + win
        if y.size - gap_start >= min_gap:
            gap_segments.append((gap_start, y.size))

    for gs, ge in gap_segments:
        seg = y[gs:ge]
        if seg.size < N_FFT:
            continue
        sf = librosa.feature.spectral_flatness(y=seg, n_fft=N_FFT, hop_length=HOP)[0]
        gap_flatnesses.append(float(np.mean(sf)))

    # -1.0 sentinel = no measurable gaps (very dense typing); skip check
    gap_flatness_median = float(np.median(gap_flatnesses)) if gap_flatnesses else -1.0

    # ---- Reject unsuitable recordings BEFORE expensive scoring ----
    n_strokes = int(len(onset_samples))
    duration_s = float(y.size / sr)
    stroke_rate = n_strokes / (duration_s + 1e-9)
    _validate_recording(
        peak_dbfs=peak_dbfs,
        clipped_fraction=clipped_fraction,
        n_strokes=n_strokes,
        stroke_rate=stroke_rate,
        mean_crest=mean_crest,
        gap_flatness_median=gap_flatness_median,
        mean_decay_ms=mean_decay_ms,
    )

    # 7) Dominant resonant peak + prominence + frequency
    peak_bin = int(np.argmax(spec_avg))
    peak_prom = float(spec_avg[peak_bin] / (spec_avg.mean() + 1e-9))
    peak_freq_hz = float(freqs[peak_bin])

    # 8) Log-spaced frequency response (32 bins, normalized 0..1 in dB)
    log_edges = np.logspace(
        np.log10(max(HPF_CUTOFF_HZ, 80.0)), np.log10(sr / 2.0), N_FREQ_RESPONSE_BINS + 1
    )
    fr = np.zeros(N_FREQ_RESPONSE_BINS, dtype=np.float32)
    for i in range(N_FREQ_RESPONSE_BINS):
        mask = (freqs >= log_edges[i]) & (freqs < log_edges[i + 1])
        if mask.any():
            fr[i] = float(spec_avg[mask].mean())
    fr_db = librosa.amplitude_to_db(fr + 1e-9, ref=max(float(fr.max()), 1e-9))
    fr_norm = np.clip((fr_db + 60.0) / 60.0, 0.0, 1.0)  # -60 dBFS → 0, 0 dB → 1

    # ---- Score mapping (0..100) ----
    # Ratios calibrated against typical mech-keyboard recordings.

    # Decay: long (>60ms) = thocky, short (<30ms) = clacky. Cap 120ms.
    decay_norm = min(mean_decay_ms / 120.0, 1.0)
    # Crest factor: ~5 = soft/sustained, ~25+ = sharp transient. Normalize 5..25.
    cf_norm = max(0.0, min((mean_crest - 5.0) / 20.0, 1.0))

    # Thock: low-band energy share weighted with decay length
    thock_combined = 0.7 * thock_ratio + 0.3 * decay_norm
    thock = _to_score(thock_combined, 0.05, 0.7)

    # Clack: high-band energy share weighted with crest factor
    clack_combined = 0.7 * clack_ratio + 0.3 * cf_norm
    clack = _to_score(clack_combined, 0.05, 0.7)

    # Creaminess: low spectral flatness (tonal, not noisy) + low metallic content
    creaminess_raw = (1.0 - flatness_mean) - metal_ratio * 0.5
    creaminess = _to_score(creaminess_raw, 0.4, 0.95)

    # Pitch: blend spectral centroid (avg energy) and dominant resonant peak (Hz)
    pitch_hz = 0.5 * centroid_mean + 0.5 * peak_freq_hz
    pitch = _to_score(pitch_hz, 500.0, 4000.0)

    # Consistency: lower CV across strokes = higher score
    consistency = _to_score(1.0 - min(cv * 2.0, 1.0), 0.0, 1.0)

    # Tonal balance: 50 = even, <50 = bass-heavy, >50 = treble-heavy
    tonal_balance = _to_score(clack_ratio - thock_ratio, -0.5, 0.5)

    # Peak resonance: prominence of dominant peak vs mean
    peak_resonance = _to_score(peak_prom, 1.0, 10.0)

    # Purity: inverse spectral flatness (1.0 = pure tone, 0.0 = white noise)
    purity = _to_score(1.0 - flatness_mean, 0.5, 0.98)

    # Peak loudness: raw dBFS pre-normalization (-40..0)
    peak_loudness = _to_score(peak_dbfs, -40.0, 0.0)

    # Metallic resonance: 3-6 kHz energy share (spring/leaf ping range)
    metallic_resonance = _to_score(metal_ratio, 0.0, 0.4)

    # Variance: stroke-to-stroke centroid spread (Hz)
    variance = _to_score(c_std, 0.0, 1500.0)

    msg = f"Analyzed {n_strokes} strokes across {duration_s:.2f}s"

    return AnalyzeResult(
        message=msg,
        thock=thock,
        clack=clack,
        creaminess=creaminess,
        pitch=pitch,
        consistency=consistency,
        tonal_balance=tonal_balance,
        peak_resonance=peak_resonance,
        purity=purity,
        peak_loudness=peak_loudness,
        metallic_resonance=metallic_resonance,
        variance=variance,
        frequency_response=[float(x) for x in fr_norm],
        verdict=None,  # TODO
    )
