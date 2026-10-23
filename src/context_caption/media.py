"""FFmpeg invocation without shell expansion; media lives only in a temporary directory."""
from pathlib import Path
import shutil
import subprocess

SUPPORTED = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".mp4", ".mov", ".mkv", ".webm"}
MAX_BYTES = 200 * 1024 * 1024
MAX_DURATION = 60 * 60


def normalize_audio(source: Path, destination: Path):
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is missing. Install it and ensure ffmpeg is on PATH.")
    if source.suffix.lower() not in SUPPORTED:
        raise ValueError("Unsupported media format.")
    if not source.is_file() or not 0 < source.stat().st_size <= MAX_BYTES:
        raise ValueError("Media must be non-empty and no larger than 200 MiB.")
    try:
        subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(source),
             "-vn", "-t", str(MAX_DURATION + 1), "-ac", "1", "-ar", "16000",
             "-c:a", "pcm_s16le", str(destination)],
            check=True, capture_output=True, timeout=300,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Audio conversion exceeded five minutes.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("FFmpeg could not decode an audio track from this file.") from exc
    import wave
    with wave.open(str(destination)) as stream:
        duration = stream.getnframes() / stream.getframerate()
    if duration <= 0 or duration > MAX_DURATION:
        raise ValueError("Use a recording between 0 seconds and 60 minutes.")
    return duration
