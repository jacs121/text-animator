import asyncio
from textAnimator.multiline import MultiTextAnimator, MultiTextMode, TextConfig

animator = MultiTextAnimator(texts=["Line 1", "Line 2"])

# Method chaining works!
animator[0]("hello", "typewriter", paint=(255, 0, 0))
animator[1]("world", "slide", paint=(0, 0, 255))

asyncio.run(animator.start())