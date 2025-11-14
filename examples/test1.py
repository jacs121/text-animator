from textAnimator import TextAnimator, Style
import asyncio
from textAnimator.modes import MODES
from textAnimator.flags import AnimatorFlags
from textAnimator.ansi import Color

animator = TextAnimator(
    "HELLO WORLD!",
    mode="slide",
    interval=0.005,
    paint=Color.GREEN.value,
    style=Style.BOLD,
    flags=AnimatorFlags.HideCursor
)
asyncio.run(animator.start())

while True:
    for color in [Color.BLUE, Color.RED, Color.YELLOW, Color.MAGENTA, Color.CYAN, Color.WHITE, Color.GREEN]:
        animator(mode=MODES.TYPEWRITER, paint=color.value, interval=0.005)
        asyncio.run(animator.start())