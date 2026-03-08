# app.py

import streamlit as st
import os
import time
from pipeline import TranslationPipeline

# --- UI Configuration ---
st.set_page_config(
    page_title="AI Civic Media Translator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff1a1a;
        box-shadow: 0 4px 8px rgba(255,75,75,0.4);
    }
    .stProgress .st-bo {
        background-color: #ff4b4b;
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e3136,#2e3136);
        color: white;
    }
    h1 {
        color: #ff4b4b;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    .card {
        background-color: #1e2127;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: Tool Documentation ---
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/artificial-intelligence.png", width=100)
    st.title("🛠️ Tech Stack & Pipeline")
    
    with st.expander("🎥 Stage 1: Ingest (FFmpeg)", expanded=False):
        st.write("**FFmpeg** is used to extract high-fidelity PCM audio and handle precise video encoding. It's the industry standard for media processing.")
        
    with st.expander("🗣️ Stage 2: ASR (Faster-Whisper)", expanded=False):
        st.write("**Faster-Whisper** provides state-of-the-art Kannada speech recognition. We use the 'small' model for high speed with localized accuracy.")
        
    with st.expander("🌐 Stage 3: Translation (Deep-Translator)", expanded=False):
        st.write("**Deep-Translator** (Google API) handles the Kannada to English mapping. It's chosen for its massive linguistic database and zero-cost tier.")
        
    with st.expander("🧠 Stage 4: Voice Cloning (XTTSv2)", expanded=False):
        st.write("**Coqui XTTSv2** is our powerhouse. It uses a 5-second sample to clone the speaker's unique vocal identity (timber, pitch, resonance).")
        
    with st.expander("🎚️ Stage 5: Audio Mixing (Pydub/Scipy)", expanded=False):
        st.write("**Pydub** mixes tracks, while **Scipy** applies custom 1-3kHz EQ dips to push the original audio into the background 'ambient' space.")
        
    with st.expander("📝 Stage 6: Subtitles (ASS Format)", expanded=False):
        st.write("**Advanced Substation Alpha (ASS)** is used instead of SRT to allow for pixel-perfect positioning, soft shadows, and mobile readability.")

    st.divider()
    st.info("Built for Scalable Civic Communication")

# --- Main Page Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🎙️ AI Media Translation Agent")
    st.subheader("Convert Kannada Civic Videos to Social-Ready English")
    
    st.markdown("""
    ### How it works:
    1. **Upload** your original Kannada civic feedback video.
    2. **Process**: Our 9-stage AI pipeline transcribes, translates, clones the voice, and mixes the audio.
    3. **Review**: Download the finalized video with burned-in subtitles and layered audio.
    """)

    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "mkv"])

with col2:
    if uploaded_file is not None:
        st.markdown("### Preview")
        st.video(uploaded_file)
        
        if st.button("🚀 Start Production Pipeline"):
            temp_dir = "workspace"
            os.makedirs(temp_dir, exist_ok=True)
            in_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(in_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # --- Pipeline execution ---
            status_container = st.empty()
            progress_bar = st.progress(0)
            
            try:
                pipeline = TranslationPipeline(work_dir=temp_dir)
                
                # We simulate progress because the pipeline is one synchronous block
                # Real progress would require callback hooks in pipeline.py
                status_container.info("🔄 Stage 1-4: AI Transcription & Translation...")
                progress_bar.progress(30)
                
                results = pipeline.run(in_path)
                
                progress_bar.progress(100)
                status_container.success("✅ Translation Pipeline Complete!")
                
                # --- Result Display ---
                st.divider()
                st.markdown("### 🎬 Final Output")
                st.video(results["final_video"])
                
                with open(results["final_video"], "rb") as file:
                    st.download_button(
                        label="⬇️ Download Processed Video",
                        data=file,
                        file_name=f"translated_{uploaded_file.name}",
                        mime="video/mp4"
                    )
                
                with st.expander("📊 Quality Control Report"):
                    st.json(results["qc_report"])
                    
            except Exception as e:
                status_container.error(f"❌ Pipeline Failed: {str(e)}")
                st.exception(e)
    else:
        st.warning("Please upload a video to begin the journey.")
