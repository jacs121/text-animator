import asyncio
from textAnimator import TextAnimator, MODES, AnimatorFlags

async def loading_animation():
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
  
    for frame in frames:
        print(f"\r{frame} Loading...", end="", flush=True)
        await asyncio.sleep(0.1)
  
    # Final message
    animator = TextAnimator(
        text="✅ Loading Complete!",
        mode=MODES.TYPEWRITER,
        paint=(100, 255, 100),
        flags=AnimatorFlags.AutoNewline
    )
    await animator.start()

asyncio.run(loading_animation())