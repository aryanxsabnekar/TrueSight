import streamlit as st
from analyzer.video import sample_video_frames
from PIL import Image
import io
from analyzer.features import analyze_frames, flow_instability, edge_mad
from analyzer.aggregate import weighted_score, label_from_score
import matplotlib.pyplot as plt
import numpy as np



st.set_page_config(page_title="TrueSight",page_icon="👁️",layout="wide")

st.markdown(
    """
    <style>
    /* --- Make the file uploader blue and visually clickable --- */
    section[data-testid="stFileUploader"] > div {
        border: 2px dashed #5AC8FA !important;
        border-radius: 0.75rem !important;
        background-color: rgba(90,200,250,0.15) !important;  /* light blue fill */
        padding: 1rem !important;
        transition: all 0.25s ease-in-out;
    }
    section[data-testid="stFileUploader"] > div:hover {
        background-color: rgba(90,200,250,0.25) !important;
        border-color: #7BD8FF !important;
    }

    /* --- Tone down the info banner (gray / subtle) --- */
    div[data-testid="stAlert"][class*="stAlert-info"] {
        background-color: rgba(255,255,255,0.06) !important;  /* dark gray */
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #E6F1FF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("TrueSight")
st.markdown(
    "##### AI-Generated Video Detection\n"
    "Upload a video to verify its authenticity and receive a transparent, data-driven verdict. Created for HackPSU Fall 2025 by Aryan Sabnekar")

with st.sidebar:
    st.header("⚙️ Analysis Settings")
    sampling_fps=st.slider("Sampling Rate (FPS)",1,30,5,
        help="Determines how many frames per second are analyzed. Higher values improve accuracy but also increase processing time.")
    
    max_frames=st.slider("Maximum Frames",15, 500, 65, step=5,
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
    st.markdown('<div class="truesight-cta">📁 Upload a video of your choice above to start the analysis.</div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


analyze_clicked=st.button("Analyze video",type="primary",disabled=(uploaded is None))

if uploaded is not None and analyze_clicked:
    with st.spinner("Sampling frames…"):
        data=sample_video_frames(uploaded,sampling_fps=sampling_fps,max_frames=max_frames)
    
    with st.spinner("Computing forensic features…"):
        frames=data["frames"]
        analysis=analyze_frames(frames)
        summary=analysis["summary"]

        flow_vals,emad_vals=[],[]
        for i in range(1,len(frames)):
            prev_f=np.asarray(frames[i-1])
            curr_f=np.asarray(frames[i])
            flow_vals.append(flow_instability(prev_f,curr_f))
            emad_vals.append(edge_mad(prev_f,curr_f))

        summary["flow_mean"]=float(np.mean(flow_vals)) if flow_vals else 0.0
        summary["edge_mad_mean"]=float(np.mean(emad_vals)) if emad_vals else 0.0

        score=weighted_score(summary)
        label,style=label_from_score(score)

    if style=="error":
        verdict_box.error(f"{label}: Authenticity score: {score:.2f}")
    elif style=="warning":
        verdict_box.warning(f"{label}: Authenticity score: {score:.2f}")
    else:
        verdict_box.success(f"{label}: Authenticity score: {score:.2f}")

    details_box.markdown(
        f"""
    **Feature Summary**
    - ELA mean: `{summary['ela_mean']:.2f}`
    - FFT high-freq ratio mean: `{summary['fft_mean']:.3f}`
    - Laplacian variance mean: `{summary['lap_mean']:.1f}`
    - Drift (ELA / FFT / LAP): `{summary['ela_drift']:.2f}` / `{summary['fft_drift']:.3f}` / `{summary['lap_drift']:.1f}`
    - Flow instability mean: `{summary.get('flow_mean',0.0):.3f}`
    - Edge-change mean: `{summary.get('edge_mad_mean',0.0):.3f}`

    """)

    st.markdown("### Per-Frame Signals")
    per=analysis["per_frame"]
    x=np.arange(1,len(per)+1)
    ela=[p["ela"] for p in per]
    fft=[p["fft"] for p in per]

    fig=plt.figure()
    plt.plot(x,ela,marker="o",label="ELA")
    plt.plot(x,fft,marker="o",label="FFT high-freq ratio")
    plt.xlabel("Frame index")
    plt.ylabel("Value")
    plt.legend()
    st.pyplot(fig)

    #Here we show the 'most suspicious' 3 frames
    st.markdown("### Top Suspicious Frames (by ELA)")
    if frames:
        top_idx=np.argsort([-p["ela"] for p in per])[:3]
        cols_top=st.columns(3)
        for j,idx in enumerate(top_idx):
            try:
                cols_top[j].image(frames[idx], caption=f"Frame {idx+1} (ELA {per[idx]['ela']:.1f})")
            except Exception:
                cols_top[j].warning(f"Frame {idx+1} could not be displayed.")

    meta=data["meta"]
    st.success(
        f"Sampled **{meta['sampled_count']}** frames "
        f"( ~**{meta['sampling_fps']} fps**) | Duration ~ **{meta['duration_sec']:.1f}s** | "
        f"Native **{meta['native_fps']:.2f} fps** | Resolution **{meta['width']}×{meta['height']}**")

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
streamlit run Main.py
"""
