import streamlit as st
from analyzer.video import sample_video_frames
from PIL import Image
import io


st.set_page_config(page_title="TrueSight",page_icon="👁️",layout="wide")

st.title("TrueSight")
st.markdown(
    "##### AI-Generated Video Detection\n"
    "Upload a video to verify its authenticity and receive a transparent, data-driven verdict. Created for HackPSU Fall 2025")

with st.sidebar:
    st.header("⚙️ Analysis Settings")
    sampling_fps=st.slider("Sampling Rate (FPS)",1,5,1,
        help="Determines how many frames per second are analyzed. Higher values improve accuracy but also increase processing time.")
    
    max_frames=st.slider("Maximum Frames",16, 128, 64, step=16,
        help="Sets the total number of frames extracted for analysis. Use fewer frames for faster previews during testing.")
    
    st.caption("💡 *Tip: Start with lower values for faster analysis, especially during development.*")

uploaded=st.file_uploader("Upload a short video file (.mp4, .mov, or .avi)",type=["mp4", "mov", "avi"],
    help="Choose a short clip for best performance.")

result_col,details_col=st.columns([1,2])
verdict_box=result_col.empty()
details_box=details_col.empty()
thumbs_box=st.container()
chart_box=st.container()

if uploaded is not None:
    st.success("✅ Video successfully uploaded.")
    st.video(uploaded)
else:
    st.info("📁 Upload a video of your choice above to start the analysis.")

analyze_clicked=st.button("Analyze video",type="primary",disabled=(uploaded is None))

if uploaded is not None and analyze_clicked:
    with st.spinner("Sampling frames…"):
        data=sample_video_frames(uploaded,sampling_fps=sampling_fps,max_frames=max_frames)

    meta=data["meta"]
    st.success(
        f"Sampled **{meta['sampled_count']}** frames "
        f"( ~**{meta['sampling_fps']} fps**) | Duration ~ **{meta['duration_sec']:.1f}s** | "
        f"Native **{meta['native_fps']:.2f} fps** | Resolution **{meta['width']}×{meta['height']}**")


    verdict_box.info("Verdict: pending detection signals (next step).") #This is a placeholder for now

    details_box.write("Frame-by-frame confidence, key visual indicators, and explainability insights will appear here.") #This is also a placeholder for now

    st.markdown("### Sampled Frames")
    thumbs=data.get("thumbs",[])
    if thumbs:
        cols=st.columns(6)
        for i,jpg in enumerate(thumbs):
            try:
                img=Image.open(io.BytesIO(jpg))
                cols[i%6].image(img,caption=f"Frame {i+1}", use_container_width=True)
            except Exception as e:
                cols[i%6].warning(f"⚠️ Frame {i+1} could not be displayed.")
                st.write(e)
    else:
        st.warning("No frames were sampled. Try a different file or lower the FPS/Max Frames settings.")
        
"""
To run, type in terminal:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
streamlit run app.py
"""