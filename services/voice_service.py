import os
import torch
from pathlib import Path
from pydub import AudioSegment
from TTS.api import TTS

# PyTorch 2.6 security fix: Allow XTTS config classes to be loaded
try:
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
    from TTS.config.shared_configs import BaseDatasetConfig
    if hasattr(torch.serialization, 'add_safe_globals'):
        torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])
except ImportError:
    pass

class VoiceCloningService:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.cloned_dir = self.work_dir / "cloned_audio"
        self.cloned_dir.mkdir(exist_ok=True)
        # Assuming CUDA if available otherwise CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("[VoiceCloningService] Loading XTTSv2 Voice Cloning model... This may take a while")
        # In a real quick-start scenario, one might use edge-tts, but requirements ask for cloning
        self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)

    def extract_speaker_sample(self, reference_audio: str, start: float, end: float) -> str:
        """Extract a small clean sample of the speaker for cloning."""
        audio = AudioSegment.from_file(reference_audio)
        sample = audio[start * 1000 : end * 1000]
        
        sample_path = str(self.work_dir / f"sample_{start}_{end}.wav")
        sample.export(sample_path, format="wav")
        return sample_path

    def generate_speech(self, transcript: list, reference_audio: str, language: str = "en") -> list:
        """
        Generate speech cloned from the original speaker voice.
        Returns the transcript updated with paths to the synthetic audio segments.
        """
        print(f"[VoiceCloningService] Generating {language} speech for {len(transcript)} segments...")
        
        # We need a fallback full sample if there's no specific clear segment
        # In a robust implementation, we'd pick the cleanest 5-10s clip of the speaker
        default_sample = self.extract_speaker_sample(reference_audio, 0.0, min(10.0, 10.0)) # First 10s

        cloned_segments = []
        for i, segment in enumerate(transcript):
            text = segment.get("text", "").strip()
            if not text:
                print(f"[VoiceCloningService] Skipping empty text for segment {i}")
                continue

            out_path = str(self.cloned_dir / f"segment_{i}.wav")
            
            print(f"[VoiceCloningService] Generating segment {i}: '{text[:30]}...' using sample {default_sample}")
            
            if not os.path.exists(default_sample):
                print(f"[VoiceCloningService] ERROR: Speaker sample not found at {default_sample}")
                raise FileNotFoundError(f"Speaker sample missing: {default_sample}")

            # Use original voice to speak translated text
            try:
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav=default_sample,
                    language=language,
                    file_path=out_path
                )
            except Exception as e:
                print(f"[VoiceCloningService] TTS failed for segment {i}: {e}")
                raise e
            
            cloned_segments.append({
                "start": segment["start"],
                "audio_path": out_path
            })
            
        return cloned_segments
