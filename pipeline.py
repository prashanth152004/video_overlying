import os
from pathlib import Path
from services.video_service import VideoService
from services.speech_service import SpeechService
from services.translation_service import TranslationEngine
from services.voice_service import VoiceCloningService
from services.audio_mixer import AudioMixerEngine
from services.subtitle_service import SubtitleEngine
from services.qc_service import QualityControlEngine

class TranslationPipeline:
    def __init__(self, work_dir="./workspace"):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        
        self.video_service = VideoService(self.work_dir)
        self.speech_service = SpeechService()
        self.translation_service = TranslationEngine()
        self.voice_service = VoiceCloningService(self.work_dir)
        self.audio_mixer = AudioMixerEngine(self.work_dir)
        self.subtitle_engine = SubtitleEngine(self.work_dir)
        self.qc_engine = QualityControlEngine()

    def run(self, input_video_path: str):
        print(f"--- Starting Pipeline for {input_video_path} ---")
        
        # Stage 1: Ingest
        print("Stage 1: Video Ingest & Audio Extraction")
        audio_path, video_metadata = self.video_service.ingest_video(input_video_path)
        
        # Stage 2: Speech Recognition (Kannada)
        print("Stage 2: Kannada Speech Recognition & Diarization")
        kannada_transcript = self.speech_service.transcribe_and_diarize(audio_path, language="kn")
        
        # Stage 3: Translation
        print("Stage 3: Translation Engine (Sarvam AI / Fallback)")
        english_transcript = self.translation_service.translate_transcript(kannada_transcript, source="kn", target="en")
        
        # Stage 4: Voice Cloning & TTS
        print("Stage 4: Voice Cloning & Speech Generation")
        cloned_audio_segments = self.voice_service.generate_speech(english_transcript, reference_audio=audio_path)
        
        # Stage 5: Audio Mixing
        print("Stage 5: Audio Mixing Engine")
        mixed_audio_path = self.audio_mixer.mix_audio(
            primary_segments=cloned_audio_segments,
            secondary_audio=audio_path,
            video_duration=video_metadata['duration']
        )
        
        # Stage 6 & 7: Subtitles & Burn-in
        print("Stage 6: Subtitle Generation")
        subtitle_path = self.subtitle_engine.generate_subtitles(english_transcript)
        
        print("Stage 7: Subtitle Burn-In & Export (Stage 8)")
        final_video_path = self.video_service.render_final_video(
            input_video_path, 
            mixed_audio_path, 
            subtitle_path
        )
        
        # Stage 9: Quality Control
        print("Stage 9: Quality Control")
        qc_report = self.qc_engine.run_checks(
            video_path=final_video_path,
            transcript=english_transcript,
            audio_path=mixed_audio_path
        )
        
        print("--- Pipeline Complete ---")
        return {
            "final_video": final_video_path,
            "qc_report": qc_report,
            "transcript": english_transcript
        }
