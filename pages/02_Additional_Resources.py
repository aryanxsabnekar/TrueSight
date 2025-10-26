from pathlib import Path
import streamlit as st
import cv2, numpy as np
from PIL import Image
import os

BASE=Path(__file__).parent.resolve()
SAMPLE_LEFT=(BASE/"assets"/"samples"/"real_classroom.mp4")
SAMPLE_RIGHT=(BASE/"assets"/"samples"/"ai_hallway.mp4")

def sample_path(p):
    return str(p) if p.exists() else None

st.set_page_config(page_title="Additional Information",layout="wide")

with st.sidebar:
    st.subheader("On this page")
    section=st.radio(
        "Jump to",
        ["Learn the tells", "Compare two videos", "Teacher toolkit"],
        label_visibility="collapsed",
        index=0)
    st.divider()
    st.page_link("Main.py",label="Analyze a video")
    st.page_link("01_About.py",label="ℹ️ About")
    st.caption("Tip: Use our TrueSight Detector to assist you!")

# -------------------------------
# Helpers
# -------------------------------
def _save_upload(upload, prefix: str) -> str:
    """Save an uploaded video to a temp path and return the path."""
    if upload is None:
        return ""
    os.makedirs("tmp", exist_ok=True)
    path = os.path.join("tmp", f"{prefix}_{upload.name.replace(' ', '_')}")
    with open(path, "wb") as f:
        f.write(upload.read())
    return path

def _video_meta(path: str):
    """Return (fps, frames, duration_s)."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return 0.0, 0, 0.0
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = (frames / fps) if (fps and frames) else 0.0
    cap.release()
    return fps, frames, duration

def _frame_at_time(path: str, t_sec: float):
    """Return RGB frame at (approx) time t_sec, or None."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0, t_sec * 1000.0))
    ok, bgr = cap.read()
    cap.release()
    if not ok or bgr is None:
        return None
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

def _strip_at_fps(path: str, fps_out: int = 1, max_frames: int = 24, thumb_h: int = 80):
    """
    Sample frames at fps_out and return a single horizontal strip image.
    Keeps at most max_frames samples. Returns PIL.Image or None.
    """
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total == 0:
        cap.release()
        return None

    step = max(1.0, src_fps / float(fps_out))
    keep_at = 0.0
    i = 0
    imgs = []
    kept = 0
    while True:
        ok, bgr = cap.read()
        if not ok:
            break
        if i + 1 >= keep_at:
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            # resize thumbnail by height
            h, w = rgb.shape[:2]
            scale = thumb_h / float(h)
            thumb = cv2.resize(rgb, (int(w*scale), thumb_h), interpolation=cv2.INTER_AREA)
            imgs.append(thumb)
            kept += 1
            keep_at += step
            if kept >= max_frames:
                break
        i += 1
    cap.release()
    if not imgs:
        return None
    strip = np.concatenate(imgs, axis=1)
    return Image.fromarray(strip)

def _md_bytes(text: str) -> bytes:
    return text.encode("utf-8")

# -------------------------------
# Section renderers
# -------------------------------
def render_learn():
    st.title("Education: Learn the tells")

    st.markdown("""
Understanding AI-generated vs. real video isn’t about one magic pixel—it’s a **bundle of small cues**. Here are the most reliable things to check with your own eyes:

1. **Motion & blur feel “too perfect.”**  
   Real cameras pick up natural motion blur, rolling-shutter wobble, and tiny exposure shifts when panning. AI clips often have *stable edges* with blur that doesn’t quite match the speed of motion.

2. **Edges and textures are oddly consistent.**  
   Hair, grass, or fabric can look **over-regular** (like it was stamped on), then “pop” or **flicker** between frames. Pause on tricky areas and step a few frames forward/back.

3. **Reflections, shadows, and lighting geometry.**  
   Check mirrors, windows, glossy car paint. Do reflections line up with the scene? Are shadows too soft, too sharp, or changing in ways that don’t match the light?

4. **Hands, small objects, and background extras.**  
   Look for shape drift (fingers, earrings, glasses arms) and copy-paste patterns in crowds or trees.

5. **Audio–lip sync (if audio exists).**  
   Lips should lead or lag **consistently** by just a few frames. Sudden word-mouth mismatches or robotic consonants are a red flag.

> Tip: On the **Compare two videos** tab below, load a “real” clip and a “synthetic” clip, then use the time slider to view the same moment from both.
""")

    # Optional placeholder for 3 tiny example thumbnails you can swap later
    with st.expander("Show quick visual examples"):
        st.info("Add short example clips or GIFs here later: reflections, edge flicker, lip-sync.")

def render_compare():
    st.title("Additional Resources: Compare two videos")

    st.subheader("Step 1 — Choose videos")

    # Default to bundled samples (change names if needed)
    base = Path(__file__).parent.resolve()
    sample_left_path  = str((base / "assets" / "samples" / "real_classroom.mp4").resolve())
    sample_right_path = str((base / "assets" / "samples" / "ai_street.mp4").resolve())

    left_path  = sample_left_path  if os.path.exists(sample_left_path)  else ""
    right_path = sample_right_path if os.path.exists(sample_right_path) else ""

    # If a sample is missing, let the user upload that side (two-column UI)
    missing_left  = not left_path
    missing_right = not right_path
    if missing_left or missing_right:
        c1, c2 = st.columns(2)
        with c1:
            if missing_left:
                st.warning("Left sample not found. Upload a video instead.")
                up = st.file_uploader("Upload left video", type=["mp4", "mov", "m4v", "webm"], key="left_up")
                left_path = _save_upload(up, "left") if up else ""
            else:
                st.success(f"Using sample: {Path(sample_left_path).name}")
        with c2:
            if missing_right:
                st.warning("Right sample not found. Upload a video instead.")
                up = st.file_uploader("Upload right video", type=["mp4", "mov", "m4v", "webm"], key="right_up")
                right_path = _save_upload(up, "right") if up else ""
            else:
                st.success(f"Using sample: {Path(sample_right_path).name}")

    if not (left_path and right_path):
        st.info("Add your sample files to assets/samples/ or upload both videos to continue.")
        return

    # ---------------- Step 2 — Watch ----------------
    st.subheader("Step 2 — Watch")
    c1, c2 = st.columns(2)
    with c1:
        st.video(left_path)
    with c2:
        st.video(right_path)

    # ---------------- Meta & strips ----------------
    lf_fps, lf_frames, lf_dur = _video_meta(left_path)
    rt_fps, rt_frames, rt_dur = _video_meta(right_path)
    max_common = max(0.0, min(lf_dur, rt_dur))

    st.caption(f"Left: ~{lf_dur:.1f}s @ {lf_fps:.1f}fps • Right: ~{rt_dur:.1f}s @ {rt_fps:.1f}fps")

    st.subheader("Step 3 — Jump to the same moment")
    if max_common <= 0:
        st.warning("Could not read durations. You can still watch the videos above.")
        return

    t = st.slider("Time (seconds)",
                  min_value=0.0,
                  max_value=float(max_common),
                  value=min(3.0, float(max_common)),
                  step=0.1)

    # Extract nearest frames at time t for both videos
    lframe = _frame_at_time(left_path, t)
    rframe = _frame_at_time(right_path, t)

    # Thumbnails strip (1 fps) under each video
    st.write("Frame overview (1 fps)")
    sc1, sc2 = st.columns(2)
    with sc1:
        lstrip = _strip_at_fps(left_path, fps_out=1, max_frames=24, thumb_h=80)
        if lstrip:
            st.image(lstrip, caption="Left timeline (1 fps)", use_container_width=True)
    with sc2:
        rstrip = _strip_at_fps(right_path, fps_out=1, max_frames=24, thumb_h=80)
        if rstrip:
            st.image(rstrip, caption="Right timeline (1 fps)", use_container_width=True)

    st.write("Selected moment (same timestamp)")
    cc1, cc2 = st.columns(2)
    with cc1:
        if lframe is not None:
            st.image(lframe, caption=f"Left @ {t:.2f}s", use_container_width=True)
    with cc2:
        if rframe is not None:
            st.image(rframe, caption=f"Right @ {t:.2f}s", use_container_width=True)

    with st.expander("What to look for at this moment"):
        st.markdown("""
- **Edges & textures:** Is hair/fabric grain consistent across adjacent frames, or does it “pop”?
- **Motion blur:** Does blur level match motion speed, or do fast objects stay oddly crisp?
- **Lighting geometry:** Do shadows/reflections behave like the light sources suggest?
- **Small shapes:** Fingers, earrings, text—do they wobble or reshape unnaturally?
- **Audio–lip sync (if any):** Do mouth movements align with syllables?
        """)


def render_toolkit():
    st.title("Education: Teacher toolkit")

    st.markdown("""
This toolkit is designed for a 20–30 minute classroom activity. Students compare a **real** and an **AI-generated** clip and record what they notice using the checklist. Wrap up with a short discussion on confidence and uncertainty.
""")

    st.markdown("#### One-page checklist (copy-friendly)")
    checklist_md = """
# Video Authenticity Quick-Check

**Instructions:** Load two short clips (one real, one synthetic). For each moment you compare, note your observations.

## What to look for
- Motion blur matches the speed of movement
- Rolling-shutter wobble or natural micro-jitter
- Edges and textures don’t “pop” or flicker
- Lighting: shadows and reflections make geometric sense
- Small details (hands, jewelry, signage) stay stable
- Audio–lip sync alignment (if audio exists)

## My notes
Time ___ : _______________________________________
- Observation 1: __________________________________
- Observation 2: __________________________________
- Observation 3: __________________________________

Confidence (circle one): Low / Medium / High
"""
    st.code(checklist_md.strip(), language="markdown")
    st.download_button("⬇️ Download checklist (Markdown)", data=_md_bytes(checklist_md), file_name="truesight_checklist.md")

    st.markdown("#### Suggested activity flow")
    st.markdown("""
1. **Warm-up (3 min):** Show a 10–15s clip. Ask: *What makes this feel real?*  
2. **Hands-on (12–15 min):** In pairs, students compare two videos using the **Compare two videos** tab.  
3. **Share-out (5–8 min):** Each pair reports one convincing cue and one uncertain cue.  
4. **Wrap (2–3 min):** Emphasize uncertainty and show how automated tools can help but aren’t proof.
""")

# -------------------------------
# Router
# -------------------------------
if section == "Learn the tells":
    render_learn()
elif section == "Compare two videos":
    render_compare()
else:
    render_toolkit()
