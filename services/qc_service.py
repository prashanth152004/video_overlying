import os
import cv2
import pyloudnorm as pyln
import soundfile as sf
from typing import Dict, Any

class QualityControlEngine:
    def __init__(self):
        pass

    def check_audio_clipping(self, audio_data) -> bool:
        """Check if any sample hits absolute 0dBFS"""
        max_val = abs(audio_data).max()
        return max_val >= 1.0

    def run_checks(self, video_path: str, transcript: list, audio_path: str) -> Dict[str, Any]:
        """
        Run automated checks:
        - Subtitle overflow/timing
        - No Audio clipping
        """
        print("[QualityControlEngine] Running automated QC checks...")
        
        report = {
            "status": "PASS",
            "warnings": [],
            "errors": []
        }

        # 1. Check audio clipping
        if os.path.exists(audio_path):
            data, sr = sf.read(audio_path)
            if self.check_audio_clipping(data):
                report["warnings"].append("Audio might be clipping (hitting 0dBFS limit)")
                
        # 2. Check subtitle timing constraints
        for idx, segment in enumerate(transcript):
            duration = segment["end"] - segment["start"]
            
            if duration < 1.0:
                report["warnings"].append(f"Subtitle {idx} is less than 1 second (too fast).")
                
            if duration > 6.0:
                report["warnings"].append(f"Subtitle {idx} is longer than 6 seconds (may stall reader).")

            text = segment["text"]
            if len(text) > 80: # absolute max over 2 lines
                report["warnings"].append(f"Subtitle {idx} length exceeds 80 chars total.")

        if len(report["errors"]) > 0:
            report["status"] = "FAIL"
            
        print(f"[QualityControlEngine] QC complete. Status: {report['status']}")
        return report
