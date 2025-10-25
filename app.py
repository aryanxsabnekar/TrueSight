import streamlit as st

st.set_page_config(page_title="TrueSight",page_icon="🎥",layout="wide")

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
    verdict_box.info("Analyzing video… (results will appear here once complete)")
    details_box.write("Frame-by-frame confidence, key visual indicators, and explainability insights will be shown here.")
else:
    st.info("📁 Upload a video of your choice above to start the analysis.")

"""To run type in terminal:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
streamlit run app.py
"""