from __future__ import annotations
import math

def _clip01(x):
    return max(0.0,min(1.0,float(x)))

def _sigmoid(x:float):
    return 1.0/(1.0+math.exp(-x))

def weighted_score(summary):
    ela_n=_clip01(summary.get("ela_mean",0.0)/20.0)
    fft_n=_clip01(summary.get("fft_mean",0.0))
    lap_n=_clip01(summary.get("lap_mean",0.0)/160.0)
    drift_n=_clip01(((summary.get("ela_drift",0.0)+summary.get("fft_drift",0.0))/2.0)/10.0)

    flow_n=_clip01(summary.get("flow_mean",0.0)/3.0)
    emad_n=_clip01(summary.get("edge_mad_mean",0.0)/0.15)

    base=(0.26*ela_n+0.22*fft_n+0.16*lap_n+0.16*flow_n+0.12*emad_n+0.08*drift_n)

    lap_mean =summary.get("lap_mean",0.0)
    lap_drift=summary.get("lap_drift",0.0)
    boost=0.15*_sigmoid((lap_mean-160.0)/40.0+(lap_drift-5.0)/2.0)

    return _clip01(base+boost)

def label_from_score(score):
    """
    Map score to (label, emoji/style).
    """
    if score>=0.65:
        return ("⚠️ Likely AI-Generated","error")
    elif score>=0.35:
        return ("🟨 Inconclusive","warning")
    else:
        return ("✅ Likely Real","success")
