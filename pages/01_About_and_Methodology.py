import streamlit as st

st.set_page_config(page_title="TrueSight — About", layout="wide")

st.title("About & Methodology")
st.markdown(
    """
TrueSight helps users assess whether a video may be **AI-generated** by analyzing frame-level forensic cues and temporal consistency.

---

## How it works

1. **Frame sampling**  
   We pull out individual frames from your video (like taking snapshots every second) so we can study them closely.

2. **Frame Analysis (Image Forensics)**
    Each frame is examined using three specialized tests that look for signs of AI generation or editing:
   - **ELA (Error Level Analysis):** The image is lightly re-saved and compared to the original. Real videos change evenly, while AI-made frames often show uneven patterns or glowing outlines where details were synthesized.
   - **FFT Frequency Analysis:** We look at how textures and edges are distributed. Real footage has natural randomness, but AI frames sometimes have overly smooth or oddly repetitive details.
   - **Laplacian Variance:** This measures how sharp or detailed the frame is. Extremely low values can mean the image was smoothed by an algorithm, while big jumps in sharpness between frames can be a red flag.

   
3. **Temporal drift**  
   We then compare how these change from one frame to the next. Big or unnatural shifts can indicate the video was generated rather than filmed.

4. **Authenticity Score**  
   Finally, we combine all the results into a single score from 0 to 1.
   Closer to 0: Likely a real, untouched video
   Closer to 1: Likely AI-generated or heavily edited

---

## Score interpretation

- **0.00–0.32** → ✅ *Likely Real*  
- **0.33–0.65** → 🟨 *Inconclusive*  
- **0.66–1.00** → ⚠️ *Likely AI-Generated*

---

## Limitations & ethics

- This is only meant to support a desicion, not be absolute proof. You should always use your own judgement alongside these results.  
- The quality of the video matters. Things such as video compression, filters, or screenshots can alter important details and can affect accuracy.
- This program is intended to combat misinformation and promote digital trust.

"""
)
