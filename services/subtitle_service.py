import os
import math
from pathlib import Path

class SubtitleEngine:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir

    def format_time_vtt(self, seconds: float) -> str:
        """Format seconds into VTT timestamp Format: hh:mm:ss.millis"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int(round((seconds - int(seconds)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

    def generate_subtitles(self, transcript: list, language: str = "en") -> str:
        """
        Generate .vtt (WebVTT) file for native HTML5/Streamlit video players.
        """
        vtt_path = str(self.work_dir / f"subtitles_{language}.vtt")
        
        vtt_content = ["WEBVTT\n"]
        
        print(f"[SubtitleEngine] Generating .vtt subtitles for {language}...")
        for i, segment in enumerate(transcript):
            start = self.format_time_vtt(segment["start"])
            end = self.format_time_vtt(segment["end"])
            
            # Very basic word wrap at ~40 chars avoiding word splits mid-phrase
            words = segment["text"].split()
            lines = []
            curr_line = ""
            for word in words:
                if len(curr_line) + len(word) > 40:
                    lines.append(curr_line.strip())
                    curr_line = word + " "
                else:
                    curr_line += word + " "
            if curr_line:
                lines.append(curr_line.strip())
                
            # Restrict to 2 lines max
            lines = lines[:2]
            text_formatted = "\n".join(lines)
            
            # VTT Block:
            # 1
            # 00:00:01.000 --> 00:00:04.000
            # Text line 1
            # Text line 2
            vtt_block = f"{i+1}\n{start} --> {end}\n{text_formatted}\n"
            vtt_content.append(vtt_block)

        with open(vtt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(vtt_content))
            
        return vtt_path
