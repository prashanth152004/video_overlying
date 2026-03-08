import os
from pathlib import Path
from pydub import AudioSegment
import pyloudnorm as pyln
import soundfile as sf
import numpy as np
import scipy.signal

class AudioMixerEngine:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.mixed_dir = self.work_dir / "mixed_audio"
        self.mixed_dir.mkdir(exist_ok=True)

    def apply_eq_cut(self, audio_data, sr):
        """Apply a slight mid-frequency dip (1-3 kHz) to push Kannada behind English."""
        # Simple Butterworth bandstop filter for 1k-3k Hz
        nyquist = sr / 2.0
        low = 1000.0 / nyquist
        high = 3000.0 / nyquist
        
        b, a = scipy.signal.butter(2, [low, high], btype='bandstop')
        filtered = scipy.signal.lfilter(b, a, audio_data)
        return filtered

    def normalize_loudness(self, audio_data, sr, target_lufs):
        meter = pyln.Meter(sr)
        current_loudness = meter.integrated_loudness(audio_data)
        normalized = pyln.normalize.loudness(audio_data, current_loudness, target_lufs)
        return normalized

    def mix_audio(self, primary_segments: list, secondary_audio: str, video_duration: float) -> str:
        """
        Primary (English Cloned): Normal loudness.
        Secondary (Kannada Original): -21 LUFS relative to English, EQ dip.
        """
        print("[AudioMixerEngine] Mixing Cloned English and Original Kannada audio...")
        
        # Load secondary (Kannada)
        data_sec, sr_sec = sf.read(secondary_audio)
        if len(data_sec.shape) > 1:
            data_sec = data_sec.mean(axis=1) # force mono
            
        # Apply EQ and ducking (-21 LUFS is standard broadcast ducking)
        data_sec = self.apply_eq_cut(data_sec, sr_sec)
        data_sec = self.normalize_loudness(data_sec, sr_sec, -21.0)
        
        # Convert back to pydub for easy timeline mixing
        sec_path_temp = str(self.work_dir / "temp_sec.wav")
        sf.write(sec_path_temp, data_sec, sr_sec)
        
        background = AudioSegment.from_file(sec_path_temp)
        
        # Create a blank canvas for primary (English)
        foreground = AudioSegment.silent(duration=int(video_duration * 1000 + 2000))
        
        print(f"[AudioMixerEngine] Overlaying {len(primary_segments)} English segments...")
        for i, seg in enumerate(primary_segments):
            start_ms = int(seg["start"] * 1000)
            if not os.path.exists(seg["audio_path"]):
                print(f"[AudioMixerEngine] WARNING: Audio file missing for segment {i}: {seg['audio_path']}")
                continue
            
            en_audio = AudioSegment.from_file(seg["audio_path"])
            print(f"[AudioMixerEngine] Mixing segment {i} at {start_ms}ms (Duration: {len(en_audio)}ms)")
            foreground = foreground.overlay(en_audio, position=start_ms)
            
        # Mix them: English (foreground) + Kannada (background)
        final_mix = background.overlay(foreground)
        
        out_path = str(self.mixed_dir / "final_mixed.wav")
        final_mix.export(out_path, format="wav")
        return out_path
