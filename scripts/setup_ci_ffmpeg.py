"""Expose the wheel-bundled FFmpeg to subsequent GitHub Actions steps."""
import os
from pathlib import Path
import subprocess

import imageio_ffmpeg


def main():
    executable = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    if not executable.is_file():
        raise RuntimeError("The imageio-ffmpeg wheel does not contain an FFmpeg executable.")
    # Validate the actual binary before exposing it to tests. Never skip media tests silently.
    subprocess.run([str(executable), "-version"], check=True, timeout=15)
    directory = Path(os.environ["RUNNER_TEMP"]) / "context-caption-bin"
    directory.mkdir(parents=True, exist_ok=True)
    link = directory / "ffmpeg"
    if link.is_symlink():
        if link.resolve() != executable:
            raise RuntimeError("Existing FFmpeg link points to a different executable.")
    elif link.exists():
        raise RuntimeError("FFmpeg destination already exists and is not a symlink.")
    else:
        link.symlink_to(executable)
    with Path(os.environ["GITHUB_PATH"]).open("a", encoding="utf-8") as stream:
        stream.write(str(directory) + "\n")
    print(f"CI FFmpeg ready: {executable.name}")


if __name__ == "__main__":
    main()
