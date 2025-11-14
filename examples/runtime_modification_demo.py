import asyncio
from textAnimator import TextAnimator, MODES

async def runtime_demo():
    animator = TextAnimator(text="Original")
  
    # Start with basic setup
    await asyncio.sleep(1)
  
    # Change while potentially running
    animator(text="Changed!", mode=MODES.MARQUEE, paint=(255, 0, 0))
  
    await asyncio.sleep(1)
  
    # More changes
    animator(mode=MODES.SCRAMBLE, interval=0.02)
  
    await asyncio.sleep(1)
  
    # Final state
    animator(text="Final Result!", mode=MODES.BOUNCE, paint=(0, 255, 0))
  
    await animator.start()

asyncio.run(runtime_demo())