"""Rebuild the synthetic two-voice demo using FFmpeg with the flite filter."""
from pathlib import Path
import json
import subprocess
from tempfile import TemporaryDirectory
import wave

from context_caption.schema import Caption, Project, Word


def create():
    lines = [
        ("SPEAKER_00", "slt", "Welcome to our captioning project."),
        ("SPEAKER_01", "rms", "Every speaker gets a consistent label."),
        ("SPEAKER_00", "slt", "You can edit captions and rename the voices."),
        ("SPEAKER_01", "rms", "Then export subtitles for your own media player."),
    ]
    rate = 16000
    frames = bytearray(b"\0" * rate)  # half-second lead-in, 16-bit mono
    captions = []
    with TemporaryDirectory() as directory:
        for i, (speaker, voice, text) in enumerate(lines, 1):
            part = Path(directory) / f"part{i}.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                            f"flite=text='{text}':voice={voice}", "-ar", str(rate),
                            "-ac", "1", "-c:a", "pcm_s16le", str(part)], check=True)
            with wave.open(str(part)) as stream:
                audio = stream.readframes(stream.getnframes())
            start = len(frames) / (2 * rate)
            frames.extend(audio)
            end = len(frames) / (2 * rate)
            tokens = text.split()
            step = (end - start) / len(tokens)
            words = [Word(t, start + n * step, start + (n + 1) * step, speaker)
                     for n, t in enumerate(tokens)]
            captions.append(Caption(i, start, end, speaker, text, text, words))
            frames.extend(b"\0" * rate)
    project = Project(captions, speakers={"SPEAKER_00": "Alex", "SPEAKER_01": "Sam"}, metadata={
        "mode": "demo", "duration": len(frames) / (2 * rate),
        "note": "Flite synthetic speech, predefined captions, and illustrative evenly spaced word times. "
                "No ASR, forced alignment, or speaker inference was performed.",
    })
    folder = Path(__file__).parent
    (folder / "demo_project.json").write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")
    with wave.open(str(folder / "demo.wav"), "wb") as wav:
        wav.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        wav.writeframes(frames)


if __name__ == "__main__":
    create()
