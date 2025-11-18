from enum import IntFlag, auto

class AnimatorFlags(IntFlag):
    NoFlags = 0

    HideCursor = auto()          # Hide terminal cursor during animation
    ClearLineBefore = auto()      # Clear line before each frame
    ClearScreenBefore = auto()    # Clear entire terminal before start
    ClearScreenAfter = auto()     # Clear entire terminal after complete
    KeepLastFrame = auto()        # After finishing, leave last frame (no cleanup)
    AutoNewline = auto()          # Print newline after animation stops
    ClearLineAfter = auto()   # Clear line after each frame