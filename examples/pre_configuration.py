from textAnimator import TextConfig, MODES
from textAnimator import MultiTextAnimator, MultiTextMode

# Configure each line individually
configs = [
    TextConfig(text="Red Text", paint=(255, 0, 0), mode=MODES.MARQUEE),
    TextConfig(text="Green Text", paint=(0, 255, 0), mode=MODES.BOUNCE),
    TextConfig(text="Blue Text", paint=(0, 0, 255), interval=0.02)
]

multi = MultiTextAnimator(
    lines=configs,
    coordination=MultiTextMode.STAGGERED,
    stagger_delay=0.3
)