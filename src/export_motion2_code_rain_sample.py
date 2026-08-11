"""Export Motion 2 with procedural vertical code rain inside the logo."""

from __future__ import annotations

import math
import random
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from export_animation import (
    LEFT_PATH,
    MOTION_2,
    RIGHT_PATH,
    VIEWBOX,
    interpolate_offset,
    interpolate_scalar,
    transform_polygon,
)


WIDTH = 1920
HEIGHT = 1080
LOGO_SIZE = 720
FPS = 60
DURATION = 1.8
FRAME_COUNT = round(FPS * DURATION)
BACKGROUND = (2, 5, 4)
RANDOM_SEED = 260811
OUTPUT = Path("output/steerix-loader-motion-2-fullhd-code-rain-60fps.gif")
GLYPHS = "01ABCDEF{}[]<>/\\|+-=*:#"


@dataclass(frozen=True)
class CodeColumn:
    x: int
    phase: float
    cycles: int
    trail_length: int
    glyph_seed: int


def load_code_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_path = Path("C:/Windows/Fonts/consola.ttf")
    if font_path.exists():
        return ImageFont.truetype(str(font_path), size=size)
    return ImageFont.load_default(size=size)


def make_columns() -> tuple[CodeColumn, ...]:
    generator = random.Random(RANDOM_SEED)
    cell_width = 14
    return tuple(
        CodeColumn(
            x=x,
            phase=generator.random(),
            cycles=generator.choice((1, 2, 3)),
            trail_length=generator.randint(28, 46),
            glyph_seed=generator.randrange(len(GLYPHS)),
        )
        for x in range(0, LOGO_SIZE, cell_width)
    )


def render_logo_mask(progress: float) -> Image.Image:
    supersample = 2
    scale = LOGO_SIZE / VIEWBOX * supersample
    mask = Image.new("L", (LOGO_SIZE * supersample, LOGO_SIZE * supersample), 0)
    draw = ImageDraw.Draw(mask)

    left_offset = interpolate_offset(
        MOTION_2.left_offsets, progress, MOTION_2.piece_curve
    )
    right_offset = interpolate_offset(
        MOTION_2.right_offsets, progress, MOTION_2.piece_curve
    )
    assembly_y = interpolate_scalar(
        MOTION_2.assembly_y, progress, MOTION_2.assembly_curve
    )
    angle = interpolate_scalar(MOTION_2.angle, progress, MOTION_2.assembly_curve)

    draw.polygon(
        transform_polygon(LEFT_PATH, left_offset, assembly_y, angle, scale),
        fill=255,
    )
    draw.polygon(
        transform_polygon(RIGHT_PATH, right_offset, assembly_y, angle, scale),
        fill=255,
    )
    return mask.resize((LOGO_SIZE, LOGO_SIZE), Image.Resampling.LANCZOS)


def glyph_color(trail_index: int, trail_length: int) -> tuple[int, int, int]:
    strength = 1.0 - trail_index / max(1, trail_length - 1)
    if trail_index == 0:
        return 210, 255, 222
    green = round(70 + 185 * strength**0.85)
    red = round(4 + 26 * strength**1.6)
    blue = round(12 + 60 * strength**1.1)
    return red, green, blue


def render_code_texture(
    progress: float,
    columns: tuple[CodeColumn, ...],
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> Image.Image:
    texture = Image.new("RGB", (LOGO_SIZE, LOGO_SIZE), (0, 30, 10))
    draw = ImageDraw.Draw(texture)
    loop_progress = progress % 1.0
    cell_height = 17
    glyph_phase = math.floor(loop_progress * 30)

    for column_index, column in enumerate(columns):
        period = LOGO_SIZE + column.trail_length * cell_height
        head = ((column.phase + column.cycles * loop_progress) % 1.0) * period

        for trail_index in range(column.trail_length):
            base_y = head - trail_index * cell_height
            for wrapped_y in (base_y - period, base_y, base_y + period):
                if -cell_height <= wrapped_y < LOGO_SIZE:
                    glyph_index = (
                        column.glyph_seed
                        + column_index * 5
                        + trail_index * 7
                        + glyph_phase
                    ) % len(GLYPHS)
                    draw.text(
                        (column.x, round(wrapped_y)),
                        GLYPHS[glyph_index],
                        font=font,
                        fill=glyph_color(trail_index, column.trail_length),
                    )

    return texture


def encode_frames(frame_dir: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for the Full HD sample")

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


def main() -> None:
    columns = make_columns()
    font = load_code_font(16)
    logo_position = ((WIDTH - LOGO_SIZE) // 2, (HEIGHT - LOGO_SIZE) // 2)
    denominator = max(1, FRAME_COUNT - 1)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="steerix-code-rain-") as temp_dir:
        frame_dir = Path(temp_dir)

        for frame_index in range(FRAME_COUNT):
            progress = frame_index / denominator
            mask = render_logo_mask(progress)
            texture = render_code_texture(progress, columns, font)
            logo = Image.new("RGB", (LOGO_SIZE, LOGO_SIZE), BACKGROUND)
            logo.paste(texture, (0, 0), mask)

            frame = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
            frame.paste(logo, logo_position)
            frame.save(frame_dir / f"frame-{frame_index:04d}.png")

        encode_frames(frame_dir)

    print(
        f"Motion 2 Full HD procedural code rain: {WIDTH}x{HEIGHT}, "
        f"{FRAME_COUNT} frames, {FPS}fps -> {OUTPUT}"
    )


if __name__ == "__main__":
    main()
