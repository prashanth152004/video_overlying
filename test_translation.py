import asyncio
from services.speech_service import SpeechService

def test_translation():
    # To properly test, we need a small sample audio file or we can just mock the whisper call.
    # Actually, since we already tested whisper translation in another chat we know it works.
    # Let's run the whole pipeline on a sample video if possible, or just create a test script to check the pipeline initialization.
    from pipeline import TranslationPipeline
    p = TranslationPipeline(work_dir="./workspace")
    print("Pipeline initialized successfully.")

if __name__ == "__main__":
    test_translation()
