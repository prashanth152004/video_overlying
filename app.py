# app.py

import streamlit as st
import os
import time
from pipeline import TranslationPipeline

# --- UI Configuration ---
st.set_page_config(
    page_title="National Media Translation Portal",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Indian Government Theme ---
st.markdown("""
    <style>
    /* Global Reset & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif !important;
    }

    /* Top Tricolor Banner */
    .block-container {
        border-top: 8px solid;
        border-image: linear-gradient(to right, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%) 1;
        padding-top: 2rem;
    }

    /* Light Theme Background */
    .main {
        background-color: #F8F9FA;
        color: #1A1A1A;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0;
    }
    
    /* Official Headings */
    h1, h2, h3 {
        color: #000080; /* Navy Blue */
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    h1 {
        border-bottom: 2px solid #FF9933;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* Card Styling */
    .card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 4px;
        border-left: 5px solid #000080;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* Primary Buttons (Saffron/Green accents depending on action) */
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        height: 3em;
        background-color: #138808; /* Indian Green */
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        background-color: #0F6B06;
        box-shadow: 0 4px 8px rgba(19,136,8,0.3);
        border: none;
        color: white;
    }

    /* Progress bar */
    .stProgress .st-bo {
        background-color: #000080;
    }
    
    /* Info/Warning boxes */
    .stAlert {
        border-radius: 4px;
        border-left: 4px solid #FF9933;
    }
    
    /* Top Header Official Details */
    .gov-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #F0F0F0;
        padding: 5px 20px;
        font-size: 12px;
        color: #333;
        border-bottom: 1px solid #CCC;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: Technical Architecture ---
with st.sidebar:
    st.markdown("### 🏛️ Directorate of Media Technology")
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=60)
    st.title("System Architecture")
    
    with st.expander("🎥 Stage 1: Media Ingest", expanded=False):
        st.write("Secure processing via FFmpeg for high-fidelity PCM audio extraction and video encoding protocols.")
        
    with st.expander("🗣️ Stage 2: Civic ASR Engine", expanded=False):
        st.write("Regional-optimized neural modeling (Faster-Whisper) for accurate Kannada speech recognition and timestamp generation.")
        
    with st.expander("🌐 Stage 3: Regional Translation", expanded=False):
        st.write("Integrated translation matrix mapping regional languages (Kannada) to administrative English.")
        
    with st.expander("🧠 Stage 4: Acoustic Signature Replication", expanded=False):
        st.write("Utilizing XTTSv2 frameworks to clone and synthesize vocal identity for seamless dubbing.")
        
    with st.expander("🎚️ Stage 5: Audio Mastering", expanded=False):
        st.write("Dynamic range compression and 1-3kHz EQ attenuation to embed original ambiance behind synthesized speech.")
        
    with st.expander("📝 Stage 6: Universal Accessibility Subtitles", expanded=False):
        st.write("Advanced Substation Alpha (ASS) format utilized for mobile-optimized, high-contrast captioning.")

    st.divider()
    st.info("Authorized Personnel Only. System governed by the National Data Processing Guidelines.")

# --- Main Page Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("National Portal for Civic Media Translation")
    st.subheader("Official Platform for Regional Video Processing")
    
    st.markdown("""
    ### Processing Guidelines:
    1. **Upload**: Submit the official Kannada civic feedback or address video.
    2. **Process**: The National AI Pipeline will transcribe, translate, and synthesize the English and Hindi equivalents simultaneously.
    3. **Review**: Access the finalized official broadcast file with compliant multi-track subtitles.
    """)

    uploaded_file = st.file_uploader("Upload Official Video File (.mp4, .mov)", type=["mp4", "mov", "mkv"])
    
    with st.expander("🎚️ Advanced Audio Controls", expanded=False):
        st.write("Determine the sound balance between the original source audio and the newly synthesized speech.")
        bg_lufs = st.slider(
            "Original Background Loudness (LUFS)",
            min_value=-40.0, max_value=-10.0, value=-21.0, step=1.0,
            help="Higher means louder background. -21 LUFS is standard for 'ducking' audio under speech. -40 essentially mutes the background."
        )
        fg_gain = st.slider(
            "Translated Speech Boost (dB)",
            min_value=-10.0, max_value=10.0, value=0.0, step=1.0,
            help="Increase or decrease the loudness of the AI generated translated voice."
        )

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
                pipeline = TranslationPipeline(work_dir=temp_dir, bg_lufs=bg_lufs, fg_gain=fg_gain)
                
                status_container.info("🔄 Processing National Assets (Multi-Language Generation)...")
                progress_bar.progress(30)
                
                results = pipeline.run(in_path)
                
                progress_bar.progress(100)
                status_container.success("✅ Multi-Language Media Generation Complete!")
                
                # Store results in session_state so UI interactions don't reload the pipeline
                st.session_state["pipeline_results"] = results
                st.session_state["uploaded_filename"] = uploaded_file.name
                    
            except Exception as e:
                status_container.error(f"❌ Pipeline Failed: {str(e)}")
                st.exception(e)

# --- Netflix-Style Multi-Track Player ---
if "pipeline_results" in st.session_state:
    st.divider()
    st.markdown("### 🎬 Official Output Media Player")
    
    results = st.session_state["pipeline_results"]
    
    # Player Settings
    player_col1, player_col2 = st.columns([1, 2])
    
    with player_col1:
        st.markdown("#### Media Controls")
        selected_audio = st.selectbox(
            "🗣️ Audio Track",
            options=list(results["videos"].keys()), # Original Kannada, English Dub, Hindi Dub
            index=1 # Default to English Dub
        )
        
        st.info("💡 **Subtitles**: Use the 'CC' button directly on the video player below to toggle English or Hindi subtitles on/off.")
        
        with open(results["videos"][selected_audio], "rb") as file:
            st.download_button(
                label=f"⬇️ Download {selected_audio} Video",
                data=file,
                file_name=f"{selected_audio.replace(' ', '_')}_{st.session_state['uploaded_filename']}",
                mime="video/mp4"
            )
            
    with player_col2:
        # Load the selected video dynamically
        active_video_path = results["videos"][selected_audio]
        
        # Load subtitle dictionaries
        subtitle_dict = {}
        if "en" in results["subtitles"]:
            subtitle_dict["English"] = results["subtitles"]["en"]
        if "hi" in results["subtitles"]:
            subtitle_dict["Hindi"] = results["subtitles"]["hi"]
            
        with open(active_video_path, "rb") as vf:
            st.video(
                data=vf.read(),
                format="video/mp4",
                subtitles=subtitle_dict
            )
            
    with st.expander("📊 Official Data Processing Report"):
        st.json(results["qc_report"])
