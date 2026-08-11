"""Render the two Steerix logo motions as 60fps GIF files.

Motion 1 slides the two halves diagonally together and back.
Motion 2 docks the two halves horizontally, spins, and returns.

Dependencies: Pillow and ffmpeg.
"""

from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw


VIEWBOX = 160.0
CENTER = (VIEWBOX / 2, VIEWBOX / 2)
Curve = tuple[float, float, float, float]
Offset = tuple[float, float]

LEFT_PATH = (
    (38.0, 42.0),
    (52.0, 42.0),
    (80.0, 80.0),
    (66.0, 80.0),
    (73.0, 89.0),
    (59.0, 110.0),
    (44.0, 110.0),
    (62.0, 85.0),
    (25.0, 85.0),
    (30.0, 75.0),
    (62.0, 75.0),
)
RIGHT_PATH = tuple((VIEWBOX - x, VIEWBOX - y) for x, y in LEFT_PATH)


@dataclass(frozen=True)
class MotionSpec:
    number: int
    duration: float
    left_offsets: tuple[tuple[float, Offset], ...]
    right_offsets: tuple[tuple[float, Offset], ...]
    assembly_y: tuple[tuple[float, float], ...]
    angle: tuple[tuple[float, float], ...]
    piece_curve: Curve
    assembly_curve: Curve


MOTION_1 = MotionSpec(
    number=1,
    duration=1.8,
    left_offsets=(
        (0.0, (0.0, 0.0)),
        (0.5, (3.0, 4.0)),
        (1.0, (0.0, 0.0)),
    ),
    right_offsets=(
        (0.0, (0.0, 0.0)),
        (0.5, (-3.0, -4.0)),
        (1.0, (0.0, 0.0)),
    ),
    assembly_y=((0.0, 0.0), (1.0, 0.0)),
    angle=((0.0, 0.0), (1.0, 0.0)),
    piece_curve=(0.0, 0.0, 1.0, 1.0),
    assembly_curve=(0.45, 0.0, 0.55, 1.0),
)

MOTION_2 = MotionSpec(
    number=2,
    duration=1.8,
    left_offsets=(
        (0.00, (0.0, 0.0)),
        (0.26, (7.0, 0.0)),
        (0.72, (7.0, 0.0)),
        (1.00, (0.0, 0.0)),
    ),
    right_offsets=(
        (0.00, (0.0, 0.0)),
        (0.26, (-7.0, 0.0)),
        (0.72, (-7.0, 0.0)),
        (1.00, (0.0, 0.0)),
    ),
    assembly_y=((0.0, 0.0), (1.0, 0.0)),
    angle=((0.0, 0.0), (0.26, 0.0), (0.72, 360.0), (1.0, 360.0)),
    piece_curve=(0.4, 0.0, 0.2, 1.0),
    assembly_curve=(0.65, 0.0, 0.35, 1.0),
)

MOTIONS = {1: MOTION_1, 2: MOTION_2}


def cubic_bezier_progress(value: float, curve: Curve) -> float:
    """Evaluate a CSS cubic-bezier timing curve at a normalized x value."""

    x1, y1, x2, y2 = curve
    parameter = value

    for _ in range(8):
        inverse = 1.0 - parameter
        x = (
            3 * inverse * inverse * parameter * x1
            + 3 * inverse * parameter * parameter * x2
            + parameter**3
        )
        slope = (
            3 * inverse * inverse * x1
            + 6 * inverse * parameter * (x2 - x1)
            + 3 * parameter * parameter * (1 - x2)
        )
        if abs(slope) < 1e-7:
            break
        parameter -= (x - value) / slope
        parameter = min(1.0, max(0.0, parameter))

    inverse = 1.0 - parameter
    return (
        3 * inverse * inverse * parameter * y1
        + 3 * inverse * parameter * parameter * y2
        + parameter**3
    )


def interpolate_scalar(
    keys: Sequence[tuple[float, float]], progress: float, curve: Curve
) -> float:
    for (start_time, start), (end_time, end) in zip(keys, keys[1:]):
        if progress <= end_time:
            local = (progress - start_time) / (end_time - start_time)
            eased = cubic_bezier_progress(min(1.0, max(0.0, local)), curve)
            return start + (end - start) * eased
    return keys[-1][1]


def interpolate_offset(
    keys: Sequence[tuple[float, Offset]], progress: float, curve: Curve
) -> Offset:
    for (start_time, start), (end_time, end) in zip(keys, keys[1:]):
        if progress <= end_time:
            local = (progress - start_time) / (end_time - start_time)
            eased = cubic_bezier_progress(min(1.0, max(0.0, local)), curve)
            return (
                start[0] + (end[0] - start[0]) * eased,
                start[1] + (end[1] - start[1]) * eased,
            )
    return keys[-1][1]


def transform_polygon(
    points: Sequence[Offset],
    piece_offset: Offset,
    assembly_y: float,
    angle: float,
    scale: float,
) -> list[Offset]:
    radians = math.radians(angle % 360.0)
    cosine, sine = math.cos(radians), math.sin(radians)
    transformed = []

    for source_x, source_y in points:
        x = source_x + piece_offset[0] - CENTER[0]
        y = source_y + piece_offset[1] - CENTER[1]
        rotated_x = x * cosine - y * sine
        rotated_y = x * sine + y * cosine
        transformed.append(
            (
                (CENTER[0] + rotated_x) * scale,
                (CENTER[1] + assembly_y + rotated_y) * scale,
            )
        )

    return transformed


def render_frame(
    motion: MotionSpec,
    progress: float,
    size: int,
    background: tuple[int, int, int],
    foreground: tuple[int, int, int],
) -> Image.Image:
    supersample = 4
    scale = size / VIEWBOX * supersample
    canvas = Image.new(
        "RGB",
        (size * supersample, size * supersample),
        background,
    )
    draw = ImageDraw.Draw(canvas)

    left_offset = interpolate_offset(
        motion.left_offsets, progress, motion.piece_curve
    )
    right_offset = interpolate_offset(
        motion.right_offsets, progress, motion.piece_curve
    )
    assembly_y = interpolate_scalar(
        motion.assembly_y, progress, motion.assembly_curve
    )
    angle = interpolate_scalar(motion.angle, progress, motion.assembly_curve)

    draw.polygon(
        transform_polygon(LEFT_PATH, left_offset, assembly_y, angle, scale),
        fill=foreground,
    )
    draw.polygon(
        transform_polygon(RIGHT_PATH, right_offset, assembly_y, angle, scale),
        fill=foreground,
    )

    return canvas.resize((size, size), Image.Resampling.LANCZOS)


def make_frames(
    motion: MotionSpec,
    fps: int,
    duration: float,
    size: int,
    background: tuple[int, int, int],
    foreground: tuple[int, int, int],
) -> list[Image.Image]:
    frame_count = round(fps * duration)
    denominator = max(1, frame_count - 1)
    return [
        render_frame(motion, index / denominator, size, background, foreground)
        for index in range(frame_count)
    ]


def gif_frame_delays(frame_count: int, fps: int) -> list[int]:
    """Return centisecond-compatible delays with the requested average FPS."""

    if not 1 <= fps <= 100:
        raise ValueError("GIF fps must be between 1 and 100")

    delays = []
    previous_centiseconds = 0
    for frame_number in range(1, frame_count + 1):
        cumulative_centiseconds = round(frame_number * 100 / fps)
        delays.append((cumulative_centiseconds - previous_centiseconds) * 10)
        previous_centiseconds = cumulative_centiseconds
    return delays


def save_gif(path: Path, frames: Sequence[Image.Image], fps: int) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        with tempfile.TemporaryDirectory(prefix="steerix-motion-") as temp_dir:
            frame_dir = Path(temp_dir)
            for index, frame in enumerate(frames):
                frame.save(frame_dir / f"frame-{index:04d}.png")

            subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-v",
                    "error",
                    "-framerate",
                    str(fps),
                    "-i",
                    str(frame_dir / "frame-%04d.png"),
                    "-filter_complex",
                    "[0:v]split[a][b];[a]palettegen=stats_mode=full[p];"
                    "[b][p]paletteuse=dither=sierra2_4a",
                    "-loop",
                    "0",
                    str(path.resolve()),
                ],
                check=True,
            )
        return

    frames[0].save(
        path,
        save_all=True,
        append_images=list(frames[1:]),
        duration=gif_frame_delays(len(frames), fps),
        loop=0,
        disposal=2,
        optimize=False,
    )


def parse_hex_color(value: str) -> tuple[int, int, int]:
    compact = value.removeprefix("#")
    if len(compact) != 6:
        raise argparse.ArgumentTypeError("color must use #RRGGBB")
    try:
        return tuple(int(compact[index : index + 2], 16) for index in (0, 2, 4))
    except ValueError as error:
        raise argparse.ArgumentTypeError("color must use #RRGGBB") from error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--motion", choices=("1", "2", "all"), default="all")
    parser.add_argument("--size", type=int, default=320)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--background", type=parse_hex_color, default="#05070a")
    parser.add_argument("--foreground", type=parse_hex_color, default="#ffffff")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    selected = MOTIONS.values() if args.motion == "all" else (MOTIONS[int(args.motion)],)

    for motion in selected:
        duration = args.duration if args.duration is not None else motion.duration
        frames = make_frames(
            motion,
            args.fps,
            duration,
            args.size,
            args.background,
            args.foreground,
        )
        gif_path = (
            args.output_dir
            / f"steerix-loader-motion-{motion.number}-{args.fps}fps.gif"
        )
        save_gif(gif_path, frames, args.fps)
        print(
            f"Motion {motion.number}: {args.fps}fps average, "
            f"{duration:.1f}s, {len(frames)} frames -> {gif_path}"
        )


if __name__ == "__main__":
    main()
