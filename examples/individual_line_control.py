from textAnimator.multiline import MultiTextAnimator
from textAnimator.modes import MODES

multi = MultiTextAnimator(lines=["A", "B", "C"])

# Basic modification
multi[0](paint=(255, 0, 0))      # Red for line 1

# Multiple parameters
multi[1](mode=MODES.MARQUEE, paint=(0, 255, 0), interval=0.03)

# Method chaining
multi[2](text="Modified!")(paint=(0, 0, 255))(interval=0.05)

# Runtime changes (works while potentially running)
multi[0](text="New Text!")(paint=(255, 255, 0))