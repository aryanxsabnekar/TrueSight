from __future__ import annotations

def weighted_score(summary: dict) -> float:
    """
    Combine features into a single authenticity score in [0,1],
    where higher means 'more likely AI-generated'.
    Tuned for demo; adjust after testing.
    """
    ela = summary["ela_mean"]          # typical 2–15
    fft = summary["fft_mean"]          # typical 0.2–0.7
    lap = summary["lap_mean"]          # varies with sharpness (50–4000)
    drift = (summary["ela_drift"] + summary["fft_drift"]) / 2.0

    # Normalize roughly to 0..1 ranges (heuristics for hackathon demo)
    ela_n = min(1.0, ela / 20.0)
    fft_n = float(fft)                  # already ~0..1
    # lower laplacian (smoother) => *more* suspicious; invert
    lap_n = 1.0 - min(1.0, lap / 1000.0)
    drift_n = min(1.0, drift / 10.0)

    # weights — tweak after eyeballing a few videos
    score = 0.40 * ela_n + 0.30 * fft_n + 0.20 * lap_n + 0.10 * drift_n
    return float(max(0.0, min(1.0, score)))

def label_from_score(score: float) -> tuple[str, str]:
    """
    Map score to (label, emoji/style).
    """
    if score >= 0.66:
        return ("⚠️ Likely AI-Generated", "error")
    elif score >= 0.33:
        return ("🟨 Inconclusive", "warning")
    else:
        return ("✅ Likely Real", "success")
