import asyncio
from textAnimator import TextAnimator
from textAnimator.modes import register_mode

def custom_wave_mode(text, progress):
    """Create a wave effect"""
    if progress >= 1.0:
        return text
  
    # Create wave pattern
    wave_text = ""
    for i, char in enumerate(text):
        if progress >= i / len(text):
            wave_text += char
        else:
            # Add wave effect for hidden characters
            wave_text += "~" if (i + progress * 10) % 2 < 1 else "˙"
  
    return wave_text

# Register the custom mode
register_mode("wave", custom_wave_mode)

# Use it
animator = TextAnimator(text="Wave Animation", mode="wave")
asyncio.run(animator.start())