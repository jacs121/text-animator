import asyncio
from textAnimator import TextAnimator
from textAnimator.modes import register_mode

@register_mode("reverse")
def custom_reverse_slide(text):
    """Create a reverse slide effect"""
    text = text[::-1]
    for i in range(len(text)):
        yield text[len(text)-i-1:]

# Use it
animator = TextAnimator(text="Custom Animation", mode="reverse")
asyncio.run(animator.start())