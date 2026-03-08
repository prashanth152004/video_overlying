from deep_translator import GoogleTranslator
import time

class TranslationEngine:
    def __init__(self, api_key=None):
        pass

    def translate_transcript(self, transcript: list, source="kn", target="en") -> list:
        """
        Pass-through function since translation is now handled by Whisper.
        """
        print(f"[TranslationEngine] Passing through {len(transcript)} segments (translation handled by Whisper)...")
        return transcript
