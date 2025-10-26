from pathlib import Path
import streamlit as st
import cv2, numpy as np
from PIL import Image
import os

BASE=Path(__file__).parent.resolve().parent
ROOT=Path(__file__).resolve().parent.parent
SAMPLE_LEFT=str((ROOT/"assets"/"samples"/"Realcutting.mp4"))
SAMPLE_RIGHT=str((ROOT/"assets"/"samples"/"AIcutting.mp4"))

def sample_path(p):
    return str(p) if p.exists() else None

st.set_page_config(page_title="Additional Information",layout="wide")

with st.sidebar:
    st.subheader("On this page")
    section=st.radio(
        "Jump to",
        ["Learn the tells", "Compare two videos"],
        label_visibility="collapsed",
        index=0)
    st.divider()
    st.page_link("Main.py",label="Analyze a video")
    st.page_link("pages/01_About.py", label="About")
    st.caption("Tip: Use our TrueSight Detector to assist you!")

# -------------------------------
# Helpers
# -------------------------------
def _save_upload(upload,prefix):
    """Save an uploaded video to a temp path and return the path."""
    if upload is None:
        return ""
    os.makedirs("tmp",exist_ok=True)
    path=os.path.join("tmp",f"{prefix}_{upload.name.replace(' ','_')}")
    with open(path,"wb") as f:
        f.write(upload.read())
    return path

def _video_meta(path):
    """Return (fps, frames, duration_s)."""
    cap=cv2.VideoCapture(path)
    if not cap.isOpened():
        return 0.0,0,0.0
    fps=cap.get(cv2.CAP_PROP_FPS) or 0.0
    frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration=(frames/fps) if (fps and frames) else 0.0
    cap.release()
    return fps,frames,duration

def _frame_at_time(path,t_sec):
    """Return RGB frame at (approx) time t_sec, or None."""
    cap=cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    cap.set(cv2.CAP_PROP_POS_MSEC,max(0,t_sec*1000.0))
    ok,bgr=cap.read()
    cap.release()
    if not ok or bgr is None:
        return None
    return cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)

def _strip_at_fps(path,fps_out:int=1,max_frames:int=24,thumb_h:int=80):
    """
    Sample frames at fps_out and return a single horizontal strip image.
    Keeps at most max_frames samples. Returns PIL.Image or None.
    """
    cap=cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    src_fps=cap.get(cv2.CAP_PROP_FPS) or 30.0
    total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total==0:
        cap.release()
        return None

    step=max(1.0,src_fps/float(fps_out))
    keep_at=0.0
    i=0
    imgs=[]
    kept=0
    while True:
        ok,bgr=cap.read()
        if not ok:
            break
        if i+1>=keep_at:
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            # resize thumbnail by height
            h,w=rgb.shape[:2]
            scale=thumb_h/float(h)
            thumb=cv2.resize(rgb,(int(w*scale),thumb_h),interpolation=cv2.INTER_AREA)
            imgs.append(thumb)
            kept+=1
            keep_at+=step
            if kept>=max_frames:
                break
        i+=1
    cap.release()
    if not imgs:
        return None
    strip=np.concatenate(imgs,axis=1)
    return Image.fromarray(strip)

def _md_bytes(text):
    return text.encode("utf-8")

# -------------------------------
# Section renderers
# -------------------------------
def render_learn():
    st.title("Education: Learn the tells")

    st.markdown("""
Understanding AI-generated vs. real video is about noticing a bunch of small cues. Here are the most reliable things to check with your own eyes to make sure the video is real:

1. **Motion & blur feel “too perfect.”**  
   Real cameras pick up natural motion blur and tiny exposure shifts when panning. AI clips often have *stable edges* with blur that doesn’t quite match the speed of motion.

2. **Edges and textures are oddly consistent.**  
   Hair, grass, or fabric can look **too regular** (like it was stamped on), then “pop” or **flicker** between frames. Pause on tricky areas and step a few frames forward/back to see if you notice anything.

3. **Reflections, shadows, and lighting geometry.**  
   Check mirrors, windows, glossy car paint. Do reflections line up with the scene? Are shadows too soft, too sharp, or changing in ways that don’t match the light?

4. **Hands, small objects, and background extras.**  
   Look for shapes to drift or duplicate (fingers, earrings, etc.) and copy-paste patterns in crowds or trees.

5. **Audio–lip sync (if audio exists).**  
   Lips should either match, lead, or lag **consistently** by just a few frames. If there are sudden word-mouth mismatches or robotic consonants there is a high likelyhood the video was generated.

> Tip: On the **Compare two videos** tab on the left, watch a “real” clip and a “synthetic” clip, then put these skills to use.
""")

def render_compare():
    st.title("Additional Resources: Compare two videos")

    left_path=SAMPLE_LEFT if os.path.exists(SAMPLE_LEFT) else ""
    right_path=SAMPLE_RIGHT if os.path.exists(SAMPLE_RIGHT) else ""

    missing_left,missing_right=(not left_path),(not right_path)
    if missing_left or missing_right:
        c1,c2=st.columns(2)
        with c1:
            if missing_left:
                st.warning("Left sample not found. Upload a video instead.")
                up=st.file_uploader("Upload left video", type=["mp4","mov","m4v","webm"], key="left_up")
                left_path=_save_upload(up,"left") if up else ""
            else:
                st.success(f"Using sample:{Path(SAMPLE_LEFT).name}")
        with c2:
            if missing_right:
                st.warning("Right sample not found. Upload a video instead.")
                up=st.file_uploader("Upload right video", type=["mp4","mov","m4v","webm"], key="right_up")
                right_path=_save_upload(up, "right") if up else ""
            else:
                st.success(f"Using sample:{Path(SAMPLE_RIGHT).name}")

    if not (left_path and right_path):
        st.info("Add your sample files to assets/samples/ or upload both videos to continue.")
        return

    # ---------------- Step 2 — Watch ----------------
    c1,c2=st.columns(2)
    with c1:
        st.video(left_path)
    with c2:
        st.video(right_path)

    # ---------------- Meta & strips ----------------
    lf_fps,lf_frames,lf_dur=_video_meta(left_path)
    rt_fps,rt_frames,rt_dur=_video_meta(right_path)
    max_common=max(0.0, min(lf_dur, rt_dur))

    st.caption(f"Left: Real Video | Right: AI Generated")


# -------------------------------
# Router
# -------------------------------
if section == "Learn the tells":
    render_learn()
elif section == "Compare two videos":
    render_compare()
