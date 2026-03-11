import os
from pathlib import Path
from pydub import AudioSegment
import pyloudnorm as pyln
import soundfile as sf
import numpy as np
import scipy.signal
import subprocess

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

    def mix_audio(self, primary_segments: list, secondary_audio: str, video_duration: float, bg_lufs: float = -21.0, fg_gain: float = 0.0, language: str = "en") -> tuple[str, str]:
        """
        Primary (Translated): Adjusted by fg_gain.
        Secondary (Kannada Original): Normalized to bg_lufs relative to Translated, EQ dip.
        """
        print(f"[AudioMixerEngine] Mixing Cloned Translated and Original Kannada audio (BG: {bg_lufs} LUFS, FG: {fg_gain} dB)...")
        
        # Load secondary (Kannada)
        data_sec, sr_sec = sf.read(secondary_audio)
        if len(data_sec.shape) > 1:
            data_sec = data_sec.mean(axis=1) # force mono
            
        # Apply EQ and ducking
        data_sec = self.apply_eq_cut(data_sec, sr_sec)
        
        # pyloudnorm breaks if bg volume is practically muted (e.g. padding silence). 
        # Only normalize if we aren't completely killing the background
        if bg_lufs > -40.0:
            data_sec = self.normalize_loudness(data_sec, sr_sec, bg_lufs)
        else:
            # -40 is practically silent, we can just drastically reduce it
            data_sec = data_sec * 0.01 
            
        # Convert back to pydub for easy timeline mixing
        sec_path_temp = str(self.work_dir / "temp_sec.wav")
        sf.write(sec_path_temp, data_sec, sr_sec)
        
        background = AudioSegment.from_file(sec_path_temp)
        
        # Create a blank canvas for primary (Foreground voices)
        foreground = AudioSegment.silent(duration=int(video_duration * 1000 + 2000))
        
        print(f"[AudioMixerEngine] Overlaying {len(primary_segments)} translated segments...")
        for i, seg in enumerate(primary_segments):
            start_ms = int(seg["start"] * 1000)
            end_ms = int(seg.get("end", seg["start"] + 3) * 1000) # Fallback to 3s if end is missing
            target_duration_ms = end_ms - start_ms
            
            if not os.path.exists(seg["audio_path"]):
                print(f"[AudioMixerEngine] WARNING: Audio file missing for segment {i}: {seg['audio_path']}")
                continue
                
            en_audio = AudioSegment.from_file(seg["audio_path"])
            current_duration_ms = len(en_audio)
            
            # PERFECT LIP-SYNC: Use FFmpeg atempo to stretch/compress audio to match exactly
            # We only do this if the difference is more than 5% to avoid artifacts on near-perfect matches
            duration_ratio = current_duration_ms / max(1, target_duration_ms)
            
            if abs(1.0 - duration_ratio) > 0.05 and target_duration_ms > 0:
                print(f"[AudioMixerEngine] Lip-Sync adjusting segment {i}: ratio {duration_ratio:.2f}x (Current: {current_duration_ms}ms, Target: {target_duration_ms}ms)")
                
                # FFmpeg atempo filter works between 0.5 and 100.0.
                # If ratio > 1, audio is longer than target -> atempo > 1 (speed up).
                # If ratio < 1, audio is shorter than target -> atempo < 1 (slow down).
                stretch_factor = duration_ratio
                
                # Clamp stretch to avoid extreme distortions
                stretch_factor = max(0.5, min(2.0, stretch_factor))
                
                stretched_path = str(self.work_dir / f"stretched_{i}.wav")
                ffmpeg_cmd = [
                    "ffmpeg", "-y", "-i", seg["audio_path"], 
                    "-filter:a", f"atempo={stretch_factor}", 
                    stretched_path
                ]
                try:
                    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    en_audio = AudioSegment.from_file(stretched_path)
                    print(f"[AudioMixerEngine] Success: Stretched audio to {len(en_audio)}ms")
                except Exception as e:
                    print(f"[AudioMixerEngine] WARNING: FFmpeg atempo failed for segment {i}: {e}. Submitting raw audio.")
            
            # Clarity enhancement: Normalize the generated voice audio before mixing
            # This ensures the synthesized voice is uniformly loud and punchy
            en_audio = en_audio.normalize()
            
            # Clarity Enhancement 2: High-Pass Filter
            # Removes low-end rumble/muddiness below 80Hz that XTTS sometimes generates
            en_audio = en_audio.high_pass_filter(80)
            
            # Clarity Enhancement 3: Dynamic Range Compression
            # Evens out the volume of the synthetic voice, making softer words louder 
            # and preventing loud peaks, giving it a professional "broadcast" presence.
            from pydub.effects import compress_dynamic_range
            en_audio = compress_dynamic_range(en_audio, threshold=-20.0, ratio=4.0, attack=5.0, release=50.0)
            
            # Clarity Enhancement 4: Makeup Gain
            # Compression reduces the peak volume of the audio. Normalizing it again brings the whole 
            # constrained waveform up to max volume, making it extremely punchy and clear.
            en_audio = en_audio.normalize()
            
            # Apply user-requested foreground gain on top of normalized audio
            if fg_gain != 0.0:
                en_audio = en_audio + fg_gain
                
            print(f"[AudioMixerEngine] Mixing segment {i} at {start_ms}ms (Duration: {len(en_audio)}ms)")
            foreground = foreground.overlay(en_audio, position=start_ms)
            
        # Mix them: English (foreground) + Kannada (background)
        final_mix = background.overlay(foreground)
        
        out_path_mixed = str(self.mixed_dir / f"final_mixed_{language}.wav")
        final_mix.export(out_path_mixed, format="wav")
        
        out_path_fg = str(self.mixed_dir / f"final_foreground_{language}.wav")
        foreground.export(out_path_fg, format="wav")
        
        return out_path_mixed, out_path_fg
