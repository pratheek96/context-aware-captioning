from pathlib import Path
import shutil
import tempfile
import unittest
import wave

from context_caption.media import normalize_audio


@unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is required")
class MediaTests(unittest.TestCase):
    def test_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            source, dest = Path(directory) / "stereo.wav", Path(directory) / "mono.wav"
            with wave.open(str(source), "wb") as stream:
                stream.setparams((2, 2, 8000, 0, "NONE", "not compressed"))
                stream.writeframes(b"\0" * 32000)
            self.assertEqual(normalize_audio(source, dest), 1)
            with wave.open(str(dest)) as stream:
                self.assertEqual((stream.getnchannels(), stream.getframerate()), (1, 16000))

    def test_invalid_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.mp4"
            source.write_bytes(b"not media")
            with self.assertRaises(RuntimeError):
                normalize_audio(source, Path(directory) / "out.wav")
