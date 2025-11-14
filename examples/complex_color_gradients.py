import asyncio
from textAnimator import TextAnimator

def temperature_colors(text):
    """Color text based on temperature - blue (cold) to red (hot)"""
    colors = []
    for i, char in enumerate(text):
        # Interpolate from blue to red
        ratio = i / max(len(text) - 1, 1)
        r = int(0 + ratio * 255)      # 0 to 255
        g = int(100 - ratio * 100)    # 100 to 0
        b = int(255 - ratio * 255)    # 255 to 0
        colors.append((r, g, b))
    return colors

animator = TextAnimator(text="Temperature Gradient", paint=temperature_colors)
asyncio.run(animator.start())