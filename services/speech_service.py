import os
import json
from faster_whisper import WhisperModel

class SpeechService:
    def __init__(self, model_size="small"):
        """Initialize Whisper model. Pyannote initialization is lightweight or delayed."""
        self.model_size = model_size
        print(f"[SpeechService] Loading Faster-Whisper '{model_size}' model...")
        self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        # NOTE: For full production pyannote diarization, you need a huggingface token:
        # from pyannote.audio import Pipeline
        # self.diarization_pipeline = Pipeline.from_pretrained(
        #     "pyannote/speaker-diarization-3.1", use_auth_token="YOUR_HF_TOKEN"
        # )
        self.diarization_pipeline = None

    def transcribe_and_diarize(self, audio_path: str, language="kn") -> list:
        """
        Transcribe audio and segment by speaker.
        Returns a list of dicts: { start, end, speaker_id, text }
        """
        print(f"[SpeechService] Transcribing {audio_path} in {language} with timestamps...")
        
        # Faster-Whisper settings for better segmentation and built-in translation
        segments, info = self.whisper_model.transcribe(
            audio_path, 
            beam_size=5, 
            language=language, 
            task="translate", # Added translation task
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            word_timestamps=False # word timestamps can sometimes be overkill, let's stick to segments but debug them
        )
        
        transcript = []
        for segment in segments:
            # Cross-reference segment.start with pyannote's speaker timeline
            speaker_label = "SPEAKER_01"  
            
            print(f"[SpeechService] Segment: {segment.start:.2f}s - {segment.end:.2f}s | Text: {segment.text[:30]}...")
            
            transcript.append({
                "start": segment.start,
                "end": segment.end,
                "speaker_id": speaker_label,
                "text": segment.text.strip()
            })
            
        if not transcript:
            print("[SpeechService] WARNING: No speech segments detected!")
            
        return transcript

