from textAnimator import TextAnimator
from textAnimator.flags import AnimatorFlags
import asyncio
import time

lyrics = [
    ("it's not that deep", 1),
    ("you should really watch your step", 1.35),
    0.5,
    ("don't tell me why you do it", 1.15),
    0.1,
    ("just tell me why you're upset with me", 2),
    1.25,
    ("I don't want to make a mess so please", 2),
    2,
    ("you", 0.25),
    0.1,
    "you can ",
    0.5,
    ["talk about", 0.5],
    0.1,
    ["everything you wanna say", 1.75],
]

animator = TextAnimator("", flags=AnimatorFlags.ClearLineBefore)

for line in lyrics:
    if isinstance(line, tuple):
        animator(line[0], interval=(line[1]/len(line[0])) if line[0] != "" else 0, flags=AnimatorFlags.ClearLineBefore)
        asyncio.run(animator.sync)
    elif isinstance(line, str):
        animator(line, interval=0)
        asyncio.run(animator.sync)
    elif isinstance(line, list):
        animator(line[0], interval=(line[1]/len(line[0])) if line[0] != "" else 0, flags=AnimatorFlags.KeepLastFrame)
        asyncio.run(animator.sync)
    else:
        time.sleep(line)
input()