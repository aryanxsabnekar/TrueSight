from __future__ import annotations
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

def _to_jpeg_bytes(img_rgb: np.ndarray, quality: int = 90) -> bytes:
    pil = Image.fromarray(img_rgb)
    buf = BytesIO()
    pil.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()

def _jpeg_back_to_array(jpg_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return rgb

def ela_score(img_rgb: np.ndarray, quality: int = 90) -> float:
    """
    Error Level Analysis: recompress to JPEG and measure absolute difference.
    Return mean difference (higher can indicate synthetic/edited artifacts).
    """
    jpg = _to_jpeg_bytes(img_rgb, quality=quality)
    rec = _jpeg_back_to_array(jpg)
    diff = cv2.absdiff(img_rgb, rec)
    # emphasize bright differences
    return float(diff.mean())

def fft_highfreq_ratio(img_rgb: np.ndarray, radius_frac: float = 0.12) -> float:
    """
    Ratio of energy outside a low-frequency circle in the FFT magnitude spectrum.
    AI imagery often has atypical high-frequency distributions.
    """
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    mag = np.abs(fshift)

    h, w = mag.shape
    cy, cx = h // 2, w // 2
    r = int(min(h, w) * radius_frac)

    Y, X = np.ogrid[:h, :w]
    mask = (X - cx) ** 2 + (Y - cy) ** 2 <= r ** 2

    low = mag[mask].sum() + 1e-6
    high = mag[~mask].sum() + 1e-6
    return float(high / (low + high))

def laplacian_variance(img_rgb: np.ndarray) -> float:
    """
    Blur/noise indicator; very low variance => overly smooth (often suspicious),
    erratic variance across frames => temporal inconsistency.
    """
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())

def analyze_frames(frames_rgb: list[np.ndarray]) -> dict:
    """
    Compute per-frame features + simple temporal drift stats.
    Returns:
      {
        "per_frame": [{ "ela":..., "fft":..., "lap":...}, ...],
        "summary": { "ela_mean":..., "fft_mean":..., "lap_mean":..., "drift_mean":... }
      }
    """
    feats = []
    for fr in frames_rgb:
        feats.append(dict(
            ela=ela_score(fr, quality=90),
            fft=fft_highfreq_ratio(fr, radius_frac=0.12),
            lap=laplacian_variance(fr),
        ))

    # temporal drift (mean abs diff frame-to-frame) for each scalar feature
    def drift(key: str) -> float:
        if len(feats) < 2:
            return 0.0
        diffs = [abs(feats[i][key] - feats[i-1][key]) for i in range(1, len(feats))]
        return float(np.mean(diffs))

    ela_vals = [f["ela"] for f in feats] or [0.0]
    fft_vals = [f["fft"] for f in feats] or [0.0]
    lap_vals = [f["lap"] for f in feats] or [0.0]

    summary = dict(
        ela_mean=float(np.mean(ela_vals)),
        fft_mean=float(np.mean(fft_vals)),
        lap_mean=float(np.mean(lap_vals)),
        ela_drift=drift("ela"),
        fft_drift=drift("fft"),
        lap_drift=drift("lap"),
    )
    return {"per_frame": feats, "summary": summary}
