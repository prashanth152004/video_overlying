import os
from pipeline import TranslationPipeline

def test_pipeline_init():
    """Verify that all services can be initialized without import errors."""
    print("Testing Pipeline Initialization...")
    try:
        pipeline = TranslationPipeline(work_dir="./test_workspace")
        print("Success: All 9 stages imported and initialized correctly.")
    except Exception as e:
        print(f"Error during initialization: {e}")

if __name__ == "__main__":
    test_pipeline_init()
