# National Portal for Media Translation

A production-grade, Streamlit-based AI video translation application. This pipeline automatically transcribes, translates, and dubs Kannada civic communication videos into high-quality **English** and **Hindi** videos.

### Features
* **Netflix-Style Player:** Watch videos with real-time audio track switching (Original, English Dub, Hindi Dub) and native WebVTT Closed Captions (CC) right in the browser.
* **Offline First architecture:** Uses Faster-Whisper and Coqui XTTSv2 running completely locally to ensure sensitive civic data never leaves your infrastructure. 
* **Speaker Diarization:** Identifies different speakers and assigns them unique synthesized voices.
* **Voice Cloning:** Preserves the tone and cadence of the original speaker in the translated audio.
* **Audio Ducking:** Dynamically balances the AI synthesized voice with the original background audio (broadcast standard -21 LUFS), complete with adjustable UI controls.
* **Formal Government Aesthetics:** Features a clean, accessible UI built around Indian civic standards (Tricolor accents, Roboto typography).

## System Architecture

The overarching pipeline process is completely automated:
1. **Video Ingest**: Extracts the main audio track.
2. **Speech Recognition**: (Kannada) Uses `faster-whisper` (`task="translate"`) to natively generate a highly accurate English transcript. Also runs Pyannote Diarization.
3. **Deep Translation**: Uses `deep-translator` to translate the English baseline transcript into Hindi. 
4. **Voice Synthesis**: Feeds the isolated speaker tracks into `Coqui XTTSv2` to synthetically recreate the speaker saying the new English and Hindi lines. 
5. **Audio Mixing**: Applies an EQ dip and LUFS ducking to the raw Kannada audio, placing it appropriately underneath the cloned speech track using `pydub` & `pyloudnorm`.
6. **Subtitles**: Converts transcripts to native `.vtt` WebVTT formatting.
7. **Fast Multiplexing**: Uses FFmpeg to remux the audio streams together instantaneously without expensive video re-encoding.

## Setup & Installation

**Prerequisites:**
* Python 3.11+
* FFmpeg (must be installed on the system and available in PATH)

**Installation:**
```bash
# Clone the repository
git clone https://github.com/prashanth152004/video_overlying.git
cd video_overlying

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run app.py
```
* The application will open in your default browser at `localhost:8501`. 
* Ensure your system has adequate graphical acceleration / GPU drivers installed so PyTorch/XTTSv2 can run its tensor operations rapidly.
