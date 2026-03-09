from deep_translator import GoogleTranslator
import time

class TranslationEngine:
    def __init__(self, api_key=None):
        pass

    def translate_transcript(self, transcript: list, source="en", target="en") -> list:
        """
        Translates text segments if target is not English.
        """
        if target == "en":
            print(f"[TranslationEngine] Passing through {len(transcript)} segments (translation handled by Whisper)...")
            return transcript
            
        print(f"[TranslationEngine] Translating {len(transcript)} segments to {target} using Deep-Translator...")
        translator = GoogleTranslator(source=source, target=target)
        
        translated_transcript = []
        for segment in transcript:
            original_text = segment["text"]
            
            try:
                translated_text = translator.translate(original_text)
                time.sleep(0.1) 
            except Exception as e:
                print(f"[TranslationEngine] Translation error for '{original_text}': {e}")
                translated_text = original_text # fallback
            
            if not translated_text:
                translated_text = original_text
            
            print(f"[TranslationEngine] Segment {segment['start']:.2f}s: '{original_text[:30]}...' -> '{translated_text[:30]}...'")
                
            translated_transcript.append({
                "start": segment["start"],
                "end": segment["end"],
                "speaker_id": segment["speaker_id"],
                "text": translated_text
            })
            
        return translated_transcript
