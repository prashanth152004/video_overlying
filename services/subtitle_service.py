import os
import math
from pathlib import Path

class SubtitleEngine:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir

    def format_time_ass(self, seconds: float) -> str:
        """Format seconds into ASS timestamp Format: h:mm:ss.cs"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int(round((seconds - int(seconds)) * 100))
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    def generate_subtitles(self, transcript: list) -> str:
        """
        Generate .ass (Advanced SubStation Alpha) file
        Constraints:
        - Max 2 lines
        - 32-40 chars per line
        - Roboto/Arial Sans-Serif
        - Bottom Center + Safe Margins
        - Soft black shadow
        """
        ass_path = str(self.work_dir / "subtitles.ass")
        
        # ASS Header with styling parameters
        ass_content = [
            "[Script Info]",
            "Title: English Translated Subtitles",
            "ScriptType: v4.00+",
            "WrapStyle: 1", # 1 = End-of-line word wrapping, only \N breaks
            "ScaledBorderAndShadow: yes",
            "PlayResX: 1920",
            "PlayResY: 1080",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            # Alignment 2 = Bottom Center. MarginV 60 = Safe Margin
            "Style: Default,Roboto,50,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,3,2,10,10,60,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]
        
        print("[SubtitleEngine] Generating .ass subtitles with constrained line-wrapping...")
        for segment in transcript:
            start = self.format_time_ass(segment["start"])
            end = self.format_time_ass(segment["end"])
            
            # Very basic word wrap at ~35 chars avoiding word splits mid-phrase
            words = segment["text"].split()
            lines = []
            curr_line = ""
            for word in words:
                if len(curr_line) + len(word) > 36:
                    lines.append(curr_line.strip())
                    curr_line = word + " "
                else:
                    curr_line += word + " "
            if curr_line:
                lines.append(curr_line.strip())
                
            # Restrict to 2 lines max
            lines = lines[:2]
            text_formatted = "\\N".join(lines)
            
            event_line = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text_formatted}"
            ass_content.append(event_line)

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ass_content))
            
        return ass_path
