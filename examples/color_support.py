import random
from textAnimator.animator import TextAnimator

text = "COLORS!!!!"

animator = TextAnimator(text)

# Single RGB color
animator(paint=(255, 0, 0))  # Red text

# Gradient between two colors
animator(paint=((255, 0, 0), (0, 0, 255)))  # Red to blue gradient

# Per-character colors
colors = [(255, i*10, 0) for i in range(len(text))]
animator(paint=colors)

# Custom color function
def rainbow_colors(text):
    return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in text]

animator(paint=rainbow_colors)