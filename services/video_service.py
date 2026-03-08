import os
import subprocess
import cv2
from pathlib import Path

class VideoService:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir

    def get_video_metadata(self, video_path: str) -> dict:
        """Extract frame rate, resolution, duration via OpenCV."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        cap.release()
        
        return {
            "fps": fps,
            "width": width,
            "height": height,
            "duration": duration
        }

    def ingest_video(self, input_video_path: str):
        """Extract audio using FFmpeg and gather metadata."""
        if not os.path.exists(input_video_path):
            raise FileNotFoundError(f"Video not found: {input_video_path}")
            
        metadata = self.get_video_metadata(input_video_path)
        print(f"[VideoService] Ingested video: {metadata['width']}x{metadata['height']} @ {metadata['fps']}fps, {metadata['duration']:.2f}s")
        
        audio_out_path = self.work_dir / "extracted_audio.wav"
        
        # FFmpeg extract audio: PCM 16-bit, 44100Hz mono
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1",
            str(audio_out_path)
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"[VideoService] Audio extracted to {audio_out_path}")
        
        return str(audio_out_path), metadata

    def render_final_video(self, input_video_path: str, mixed_audio_path: str, subtitle_ass_path: str) -> str:
        """Burn subtitles and mux with mixed audio using FFmpeg."""
        output_path = str(self.work_dir / "final_output.mp4")
        
        # This builds an ffmpeg command to add subtitles and replace audio stream.
        # Ensure subtitle file path is escaped for ffmpeg filter syntax
        esc_sub_path = subtitle_ass_path.replace("\\", "/").replace(":", "\\:")
        
        cmd = [
            "ffmpeg", "-y", 
            "-i", input_video_path,
            "-i", mixed_audio_path,
            "-filter_complex", f"[0:v]subtitles='{esc_sub_path}'[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
            output_path
        ]
        
        print("[VideoService] Rendering final video with subtitles...")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_path
