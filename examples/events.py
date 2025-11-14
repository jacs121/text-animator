from textAnimator.multiline import MultiTextAnimator
from textAnimator.animator import TextAnimator

# Track animation progress
async def on_complete(text):
    print(f"Completed: {text}")

async def on_frame(frame):
    print(f"Frame: {frame}")

# Single-line events
animator = TextAnimator(text="Hello World")
animator.on_complete.connect(on_complete)
animator.on_frame.connect(on_frame)

# Multi-line events
multi = MultiTextAnimator(lines=["Line 1", "Line 2"])

async def on_text_complete(line_idx):
    print(f"Line {line_idx} completed!")

async def on_all_complete(data):
    print("All lines completed!")

multi.on_text_complete.connect(on_text_complete)
multi.on_all_complete.connect(on_all_complete)