import asyncio
import random
import textAnimator
from textAnimator.multiline import TextConfig
from textAnimator.flags import AnimatorFlags

@textAnimator.register_mode("typeDeleter")
async def typeDeleter(text):
    for i in range(1, len(text) + 1):
        yield text[:-i]+" "*i

num = 4
animator = textAnimator.MultiTextAnimator([TextConfig(" ", mode="static", flags=AnimatorFlags.ClearLineBefore)]*num)
while True:
    lengths = [random.randint(2, 8) for _ in range(num)]
    lengths = [8]*num
    for i in range(num):
        animator[i](">"*lengths[i], mode="typewriter")
    asyncio.run(animator.sync)
    for i in range(num):
        animator[i](">"*lengths[i], mode="typeDeleter")
    asyncio.run(animator.sync)
    break