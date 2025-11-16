from textAnimator.multiline import MultiTextAnimator, TextConfig
import asyncio
from textAnimator.animator import TextAnimator

inter = 0.1

animator = MultiTextAnimator(
    texts=[
        TextConfig(
            text="welcome to VX1",
            mode="marquee",
            interval=inter
        ),
        TextConfig(
            text="welcome to VX1",
            mode="marquee",
            interval=inter
        )
    ]
)

async def on_frame_end(textIndex):
    if textIndex == 0:
        animator[0](interval=inter/2)

animator.on_text_complete.connect(on_frame_end)
asyncio.run(animator.sync)