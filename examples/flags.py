from textAnimator import AnimatorFlags
from textAnimator.animator import TextAnimator

# Combine flags with bitwise OR
flags = AnimatorFlags.HideCursor | AnimatorFlags.AutoNewline | AnimatorFlags.ClearScreenBefore

animator = TextAnimator(
    text="Hello World",
    flags=flags
)

# Available flags:
# - NoFlags: No special behavior
# - HideCursor: Hide cursor during animation
# - ShowCursor: Show cursor (default)
# - ClearScreenBefore: Clear screen before starting
# - ClearScreenAfter: Clear screen after completing
# - AutoNewline: Add newline after completion
# - KeepAnimation: Keep final frame displayed