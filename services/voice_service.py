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
        """Extract a small clean sample of the speaker for cloning, filtering out background noise."""
        audio = AudioSegment.from_file(reference_audio)
        sample = audio[start * 1000 : end * 1000]
        
        # Pre-process the reference sample so the AI doesn't clone background noise/muddiness
        # 1. Normalize the volume so the model hears the voice clearly
        sample = sample.normalize()
        # 2. High-pass filter to remove low rumble, wind noise, mic bumps
        sample = sample.high_pass_filter(100)
        # 3. Low-pass filter to remove high-frequency background hiss/static
        sample = sample.low_pass_filter(8000)
        
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
            
            # Extract a dynamic sample for this specific segment to better match the current speaker's tone
            segment_duration = segment["end"] - segment["start"]
            current_sample = default_sample
            if segment_duration >= 3.0:
                 # XTTS prefers >3s samples for good cloning. Grab exactly what they said here.
                 try:
                     current_sample = self.extract_speaker_sample(reference_audio, segment["start"], segment["end"])
                 except Exception as e:
                     print(f"[VoiceCloningService] Failed to extract dynamic sample for segment {i}, falling back to default. Error: {e}")
            
            print(f"[VoiceCloningService] Generating segment {i}: '{text[:30]}...' using sample {current_sample}")
            
            if not os.path.exists(current_sample):
                print(f"[VoiceCloningService] ERROR: Speaker sample not found at {current_sample}")
                raise FileNotFoundError(f"Speaker sample missing: {current_sample}")

            # Use original voice to speak translated text
            try:
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav=current_sample,
                    language=language,
                    file_path=out_path
                )
            except Exception as e:
                print(f"[VoiceCloningService] TTS failed for segment {i}: {e}")
                raise e
            
            cloned_segments.append({
                "start": segment["start"],
                "end": segment["end"], # Ensure 'end' is passed along for downstream lip-sync
                "audio_path": out_path
            })
            
        return cloned_segments
