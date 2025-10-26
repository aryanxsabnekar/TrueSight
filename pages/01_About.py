import streamlit as st

st.set_page_config(page_title="TrueSight | About",layout="wide")

with st.sidebar:
    st.subheader("On this page")
    st.markdown(
        """
- [How it works](#how-it-works)
- [Score interpretation](#score-interpretation)
- [Limitations and Future Plans](#limitations-and-future-plans)
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("Click to jump between sections.")

st.title("About")
st.markdown(
    """
Built for HackPSU 2025, TrueSight is a tool that helps users assess whether a video may be **AI-generated** by analyzing frame-level forensic cues and consistency.

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
- **0.33–0.65** → ⚠️ *Inconclusive*  
- **0.66–1.00** → 🛑 *Likely AI-Generated*

---

## Limitations and Future Plans

- This is only meant to support a decision, not be absolute proof. You should always use your own judgement alongside these results.  
- The quality of the video matters. Things such as video compression, filters, or screenshots can alter important details and can affect accuracy.
- This program is intended to combat misinformation and promote digital trust.

### How to Improve the Classifier

I'm focused on making the detector both smarter with motion and confident in its choice, especially as hyper-real generators such as Sora2 get better.

- It will learn from motion not just snapshots. To do this we will add sequence models and optical-flow cues so the system notices subtle frame-to-frame tells (tiny flickers, texture “pops”, and micro-details) that single-frame checks miss.
- It will also prioritize looking where it matters. By tracking faces and other key objects in a video, we can score those regions separately instead of averaging everything together.
- It will also take advantage of sounds in videos. If the videos have audio, we'll compare lip movement and speech timing to catch weird Audio/Video mismatches.
- It will be trained on tougher, more realistic data from premium generators. I will include hyper-real generated clips and lots of common edits (filters or crop resizes) to the data it is trained on.
- It will also be upfront about uncertainty. Many text AI checkers are quick to clear or condemn writing but for this video checker, we’ll compute a score, show its confidence, and do our best to be upfront.




"""
)
