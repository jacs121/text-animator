import asyncio
from textAnimator import MultiTextAnimator, MultiTextMode, TextConfig, AnimatorFlags

async def colorful_menu():
    menu = MultiTextAnimator(
        lines=[
            TextConfig("1. Start Game", paint=(100, 255, 100)),
            TextConfig("2. Settings", paint=(100, 200, 255)),
            TextConfig("3. Exit", paint=(255, 100, 100)),
        ],
        coordination=MultiTextMode.STAGGERED,
        stagger_delay=0.3,
        default_flags=AnimatorFlags.HideCursor | AnimatorFlags.AutoNewline
    )
    await menu.start()

asyncio.run(colorful_menu())