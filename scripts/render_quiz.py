"""Render a vertical, white-and-blue ざつなクイズ Short.

The question is generated deterministically from the current day.  It uses
simple arithmetic only, so each answer can be verified in the source.
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
WHITE, NAVY, BLUE, PALE = (255, 255, 255), (18, 59, 111), (37, 116, 205), (235, 245, 255)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def font(size: int):
    return ImageFont.truetype(FONT, size)


def centered(draw, value, y, size, color=NAVY):
    box = draw.textbbox((0, 0), value, font=font(size))
    draw.text(((W - (box[2] - box[0])) / 2, y), value, font=font(size), fill=color)


def stick(draw, pose: str):
    # Intentionally rough, hand-drawn-looking guide character.
    x, y = 840, 1280
    draw.ellipse((x - 95, y - 95, x + 95, y + 95), fill=WHITE, outline=NAVY, width=15)
    draw.ellipse((x - 35, y - 8, x - 18, y + 16), fill=BLUE)
    draw.ellipse((x + 18, y - 8, x + 35, y + 16), fill=BLUE)
    draw.arc((x - 25, y + 15, x + 25, y + 55), 10, 170, fill=NAVY, width=8)
    draw.line((x, y + 95, x, y + 275), fill=NAVY, width=18)
    draw.line((x, y + 275, x - 65, y + 390), fill=NAVY, width=18)
    draw.line((x, y + 275, x + 70, y + 390), fill=NAVY, width=18)
    if pose == "point":
        draw.line((x - 4, y + 140, x - 145, y + 65), fill=NAVY, width=18)
        draw.line((x - 145, y + 65, x - 185, y + 35), fill=NAVY, width=12)
        draw.line((x + 4, y + 140, x + 85, y + 170), fill=NAVY, width=18)
    else:
        draw.line((x - 4, y + 140, x - 100, y + 110), fill=NAVY, width=18)
        draw.line((x + 4, y + 140, x + 95, y + 90), fill=NAVY, width=18)


def render_frame(path: Path, question: str, footer: str, pose: str):
    im = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, W, 220), fill=PALE)
    draw.rectangle((0, 208, W, 220), fill=BLUE)
    centered(draw, "3秒 ざつなクイズ", 65, 60)
    draw.rounded_rectangle((70, 355, 1010, 1010), radius=38, fill=WHITE, outline=BLUE, width=11)
    centered(draw, question, 590, 100, BLUE)
    centered(draw, footer, 1650, 76, NAVY)
    stick(draw, pose)
    im.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    # Verified identity: (n + 7) × 3 = n×3 + 21.
    n = (dt.date.today().toordinal() % 7) + 4
    question = f"（{n} + 7）× 3 = ？"
    answer = (n + 7) * 3
    q, a = args.output / "question.png", args.output / "answer.png"
    render_frame(q, question, "答えはコメントで！", "point")
    render_frame(a, f"答え：{answer}", "分配法則で解ける！", "explain")
    # Direct cuts keep the text crisp rather than slowly fading.
    concat = args.output / "frames.txt"
    concat.write_text(f"file '{q.name}'\nduration 4\nfile '{a.name}'\nduration 4\nfile '{a.name}'\n", encoding="utf-8")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat.name,
        "-vf", "fps=30,format=yuv420p", "-r", "30", "-c:v", "libx264",
        "-movflags", "+faststart", "final.mp4",
    ], cwd=args.output, check=True)
    (args.output / "metadata.txt").write_text(
        f"【3秒クイズ】{question} #shorts\n\n答え：{answer}。分配法則で確認できる、計算クイズです。\n#クイズ #数学 #ざつなクイズ\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

