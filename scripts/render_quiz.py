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

# Reviewed, original wording. Rotate category daily without repeating questions.
QUIZZES = [
    ("思い込み", "2位の人を追い抜いた。\n今、あなたは何位？", "2位", "相手の2位に入る。\n1位はまだ前にいる。", None),
    ("図形・配置", "この図の中に\n正方形はいくつ？", "5個", "小さい4個に加えて、\n外側の大きな1個。", "grid"),
    ("論理", "AはBより前。\nCはAより前。\n3人の最後尾は誰？", "B", "前から C → A → B。\nだから最後尾はB。", None),
    ("思い込み", "5台で5分に5個作る。\n同じ機械100台なら\n100個作るのに何分？", "5分", "1台が5分で1個。\n100台が同時に作れる。", None),
    ("図形・配置", "この図の中に\n三角形はいくつ？", "3個", "左右に小さい2個。\n全体で大きな1個。", "triangle"),
    ("論理", "赤・青・白の箱。\n鍵は赤にはない。\n青にもない。どの箱？", "白い箱", "候補は3つ。\n赤と青を除くと白だけ。", None),
    ("思い込み", "池の葉が毎日2倍に。\n20日目に池いっぱい。\n半分だったのは何日目？", "19日目", "19日目の半分が、\n翌日に2倍でいっぱい。", None),
    ("図形・配置", "3×3のマス目。\n正方形は全部でいくつ？", "14個", "1×1が9個、2×2が4個。\n3×3が1個。合計14個。", "grid3"),
    ("論理", "A・B・Cが並ぶ。\nBは両端ではない。\nAはCより左。並び順は？", "A → B → C", "Bは中央に決まる。\n左がA、右がCになる。", None),
]


def quiz_for_day(day):
    index = (day - dt.date(2026, 10, 10)).days
    if not 0 <= index < len(QUIZZES):
        raise RuntimeError("Reviewed quiz queue exhausted; add new questions before uploading.")
    return QUIZZES[index]


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


def render_frame(path: Path, question: str, footer: str, pose: str, category="", diagram=None, remaining=None):
    im = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, W, 220), fill=PALE)
    draw.rectangle((0, 208, W, 220), fill=BLUE)
    centered(draw, f"ざつなクイズ｜{category}", 65, 60)
    draw.rounded_rectangle((70, 355, 1010, 1010), radius=38, fill=WHITE, outline=BLUE, width=11)
    lines = question.splitlines()
    size = 64
    while any(draw.textbbox((0, 0), line, font=font(size))[2] > 840 for line in lines):
        size -= 2
    for i, line in enumerate(lines):
        centered(draw, line, 440 + i * (size + 25), size, BLUE)
    if diagram:
        if diagram.startswith("grid"):
            n = 3 if diagram == "grid3" else 2
            for i in range(n + 1):
                p = 390 + i * 300 // n
                draw.line((p, 700, p, 1000), fill=NAVY, width=8)
                draw.line((390, 700 + i * 300 // n, 690, 700 + i * 300 // n), fill=NAVY, width=8)
        else:
            draw.line((540, 700, 360, 990, 720, 990, 540, 700), fill=NAVY, width=8)
            draw.line((540, 700, 540, 990), fill=NAVY, width=8)
    for i, line in enumerate(footer.splitlines()):
        centered(draw, line, 1620 + i * 80, 56, NAVY)
    stick(draw, pose)
    if remaining is not None:
        draw.ellipse((390, 1110, 610, 1330), fill=PALE, outline=BLUE, width=10)
        centered(draw, str(remaining), 1150, 100, BLUE)
        draw.rounded_rectangle((120, 1440, 700, 1460), radius=10, fill=PALE)
        draw.rounded_rectangle((120, 1440, 120 + 580 * remaining // 5, 1460), radius=10, fill=BLUE)
    im.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--date", type=dt.date.fromisoformat)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    day = args.date or dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date()
    category, question, answer, explanation, diagram = quiz_for_day(day)
    q, a = args.output / "question.png", args.output / "answer.png"
    render_frame(q, question, "ひらめいたら答えて！", "point", category, diagram)
    render_frame(a, f"答え：{answer}", explanation, "explain", category, diagram)
    # Direct cuts keep the text crisp rather than slowly fading.
    concat = args.output / "frames.txt"
    frames = [f"file '{q.name}'\nduration 3\n"]
    for remaining in range(5, 0, -1):
        countdown = args.output / f"countdown-{remaining}.png"
        render_frame(countdown, question, "答え、決まった？", "point" if remaining % 2 else "explain", category, diagram, remaining)
        frames.append(f"file '{countdown.name}'\nduration 1\n")
    frames.append(f"file '{a.name}'\nduration 4\nfile '{a.name}'\n")
    concat.write_text("".join(frames), encoding="utf-8")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat.name,
        "-vf", "fps=30,format=yuv420p", "-r", "30", "-c:v", "libx264",
        "-movflags", "+faststart", "final.mp4",
    ], cwd=args.output, check=True)
    (args.output / "metadata.txt").write_text(
        f"【{category}クイズ】{question.replace(chr(10), '')} #shorts\n\n答え：{answer}\n{explanation}\n#クイズ #ひらめき #ざつなクイズ\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

