from textAnimator import MODES
from textAnimator.animator import TextAnimator
from textAnimator.modes import register_mode

# Use built-in modes
animator = TextAnimator(text="Example", mode=MODES.SCRAMBLE)

# Or use string names
animator = TextAnimator(text="Example", mode="typewriter")

# Register custom modes
def custom_mode(text, progress):
    # Your custom animation logic
    return

register_mode("custom", custom_mode)
animator = TextAnimator(text="Example", mode="custom")