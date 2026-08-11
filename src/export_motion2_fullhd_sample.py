"""Export a Full HD Motion 2 sample with a random color on every frame."""

from __future__ import annotations

import colorsys
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from export_animation import MOTION_2, render_frame


WIDTH = 1920
HEIGHT = 1080
LOGO_SIZE = 640
FPS = 60
DURATION = 1.8
RANDOM_SEED = 20260811
BACKGROUND = (5, 7, 10)
OUTPUT = Path("output/steerix-loader-motion-2-fullhd-random-60fps.gif")


def vivid_random_color(generator: random.Random) -> tuple[int, int, int]:
    hue = generator.random()
    saturation = generator.uniform(0.72, 1.0)
    value = generator.uniform(0.9, 1.0)
    red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
    return round(red * 255), round(green * 255), round(blue * 255)


def main() -> None:
    frame_count = round(FPS * DURATION)
    denominator = max(1, frame_count - 1)
    generator = random.Random(RANDOM_SEED)
    position = ((WIDTH - LOGO_SIZE) // 2, (HEIGHT - LOGO_SIZE) // 2)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for the Full HD sample")

    with tempfile.TemporaryDirectory(prefix="steerix-fullhd-") as temp_dir:
        frame_dir = Path(temp_dir)

        for index in range(frame_count):
            color = vivid_random_color(generator)
            logo = render_frame(
                MOTION_2,
                index / denominator,
                LOGO_SIZE,
                BACKGROUND,
                color,
            )
            frame = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
            frame.paste(logo, position)
            frame.save(frame_dir / f"frame-{index:04d}.png")

        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-v",
                "error",
                "-framerate",
                str(FPS),
                "-i",
                str(frame_dir / "frame-%04d.png"),
                "-filter_complex",
                "[0:v]split[a][b];[a]palettegen=stats_mode=full[p];"
                "[b][p]paletteuse=dither=sierra2_4a",
                "-loop",
                "0",
                str(OUTPUT.resolve()),
            ],
            check=True,
        )
    print(
        f"Motion 2 Full HD random-color sample: {WIDTH}x{HEIGHT}, "
        f"{frame_count} frames, {FPS}fps -> {OUTPUT}"
    )


if __name__ == "__main__":
    main()
