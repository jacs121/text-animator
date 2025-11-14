# TextAnimator - Terminal Text Animation Library

A powerful Python library for creating beautiful terminal text animations with single-line and multi-line support, individual line control, and extensive customization options.

![TextAnimator Demo](https://img.shields.io/badge/Python-3.7+-blue.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg) ![Terminal](https://img.shields.io/badge/Terminal-Ansi--Codes-red.svg)

## Features

### Core Features

- **5 Built-in Animation Modes**: Typewriter, Marquee, Bounce, Scramble, Slide
- **Runtime Modification**: Change any parameter on-the-fly using `__call__`
- **Method Chaining**: Chain multiple modifications for concise code
- **Color Support**: RGB colors, gradients, and per-character coloring
- **Style Support**: Bold, italic, underline, and more
- **Event System**: Track animation progress and completion
- **Custom Flags**: Control cursor behavior, screen clearing, and more

### Multi-Line Animations

- **Multiple Coordination Modes**: Simultaneous, Staggered, Sequential
- **Individual Line Control**: Granular control with `animator[0](parameter=value)` pattern
- **Per-Line Customization**: Different modes, colors, speeds for each line
- **Line Spacing**: Add blank lines between animated text
- **Runtime Line Modification**: Change lines while animations are running

### 🔧 Advanced Features

- **Custom Animation Modes**: Register your own animation patterns
- **Async/Await Support**: Full async support for modern Python
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **No Dependencies**: Pure Python, no external packages required

---

### Basic Single-Line Animation

```python
import asyncio
from textAnimator import TextAnimator, MODES

# Simple typewriter animation
animator = TextAnimator(
    text="Hello, World!",
    mode=MODES.TYPEWRITER
)
await animator.start()
```

### Runtime Modification

```python
# Create animator
animator = TextAnimator(text="Original Text")

# Modify parameters on-the-fly
animator(text="New Text", mode=MODES.MARQUEE, paint=(255, 0, 0))

# Method chaining works too!
animator(text="Chained!")(mode=MODES.BOUNCE)(interval=0.02)

await animator.start()
```

### Multi-Line Animation

```python
from textAnimator import MultiTextAnimator, MultiTextMode

# Simple multi-line animation
multi = MultiTextAnimator(
    lines=["Line 1", "Line 2", "Line 3"],
    coordination=MultiTextMode.SIMULTANEOUS
)
await multi.start()
```

### Individual Line Control

```python
# Granular control with indexing pattern
multi = MultiTextAnimator(
    lines=["Red Line", "Green Line", "Blue Line"],
    default_mode=MODES.TYPEWRITER
)

# NEW PATTERN: animator[index](parameter=value)
multi[0](paint=(255, 0, 0))      # Red for first line
multi[1](paint=(0, 255, 0))      # Green for second line
multi[2](paint=(0, 0, 255))      # Blue for third line

# Different modes per line
multi[0](mode=MODES.MARQUEE)
multi[1](mode=MODES.BOUNCE)
multi[2](mode=MODES.SCRAMBLE)

# Method chaining on individual lines
multi[0](text="Custom Text")(paint=(255, 100, 200))(interval=0.03)

await multi.start()
```

---

## 📖 Documentation

### Animation Modes


| Mode         | Description                                     | Example                   |
| -------------- | ------------------------------------------------- | --------------------------- |
| `TYPEWRITER` | Reveals text character by character             | Classic typing effect     |
| `MARQUEE`    | Text scrolls horizontally                       | News ticker style         |
| `BOUNCE`     | Text bounces in from edges                      | Dynamic entrance          |
| `SCRAMBLE`   | Text appears as random characters then resolves | Mystery/encryption effect |
| `SLIDE`      | Text slides in from one side                    | Smooth entrance           |

```python
from textAnimator import MODES

# Use built-in modes
animator = TextAnimator(text="Example", mode=MODES.SCRAMBLE)

# Or use string names
animator = TextAnimator(text="Example", mode="typewriter")

# Register custom modes
def custom_mode(text, progress):
    # Your custom animation logic
    return partial_text

register_mode("custom", custom_mode)
animator = TextAnimator(text="Example", mode="custom")
```

### Color Support

```python
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
```

### Multi-Line Coordination Modes

#### 1. **SIMULTANEOUS** - All lines at once

```python
multi = MultiTextAnimator(
    lines=["Line 1", "Line 2", "Line 3"],
    coordination=MultiTextMode.SIMULTANEOUS
)
# All three lines start animating at the same time
```

#### 2. **STAGGERED** - Delayed starts

```python
multi = MultiTextAnimator(
    lines=["Line 1", "Line 2", "Line 3"],
    coordination=MultiTextMode.STAGGERED,
    stagger_delay=0.5  # 0.5 second delay between each line
)
# Line 1 starts immediately, Line 2 starts after 0.5s, Line 3 after 1.0s
```

#### 3. **SEQUENTIAL** - One after another

```python
multi = MultiTextAnimator(
    lines=["Line 1", "Line 2", "Line 3"],
    coordination=MultiTextMode.SEQUENTIAL
)
# Line 1 completes, then Line 2 starts, then Line 3
```

### Individual Line Control

The `animator[index]()` pattern gives you granular control over each line:

```python
multi = MultiTextAnimator(lines=["A", "B", "C"])

# Basic modification
multi[0](paint=(255, 0, 0))      # Red for line 1

# Multiple parameters
multi[1](mode=MODES.MARQUEE, paint=(0, 255, 0), interval=0.03)

# Method chaining
multi[2](text="Modified!")(paint=(0, 0, 255))(interval=0.05)

# Runtime changes (works while potentially running)
multi[0](text="New Text!")(paint=(255, 255, 0))
```

**Available parameters for individual line control:**

- `text`: Change the text content
- `mode`: Animation mode for this line
- `interval`: Animation speed for this line
- `paint`: Color/gradient for this line
- `style`: Text style for this line
- `flags`: Animator flags for this line

### TextConfig for Pre-Configuration

```python
from textAnimator import TextConfig

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
```

### Event System

```python
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

async def on_line_complete(line_idx):
    print(f"Line {line_idx} completed!")

async def on_all_complete(data):
    print("All lines completed!")

multi.on_line_complete.connect(on_line_complete)
multi.on_all_complete.connect(on_all_complete)
```

### Animator Flags

```python
from textAnimator import AnimatorFlags

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
```

## Examples

### Example 1: Colorful Menu

```python
import asyncio
from textAnimator import MultiTextAnimator, MultiTextMode, TextConfig, AnimatorFlags

async def colorful_menu():
    menu = MultiTextAnimator(
        lines=[
            TextConfig("1. Start Game", paint=(100, 255, 100)),
            TextConfig("2. Settings", paint=(100, 200, 255)),
            TextConfig("3. Exit", paint=(255, 100, 100)),
        ],
        coordination=MultiTextMode.STAGGERED,
        stagger_delay=0.3,
        default_flags=AnimatorFlags.HideCursor | AnimatorFlags.AutoNewline
    )
    await menu.start()

asyncio.run(colorful_menu())
```

### Example 2: Status Dashboard

```python
from textAnimator import MultiTextAnimator, MultiTextMode, AnimatorFlags

async def status_dashboard():
    dashboard = MultiTextAnimator(
        lines=[
            "Database: Connected",
            "API: Online", 
            " Cache: Degraded",
            "Mail Server: Offline"
        ],
        coordination=MultiTextMode.STAGGERED,
        stagger_delay=0.2,
        default_paint=(255, 255, 255),
        default_flags=AnimatorFlags.HideCursor
    )
  
    # Customize individual lines
    dashboard[0](paint=(100, 255, 100))  # Green for success
    dashboard[1](paint=(100, 255, 100))  # Green for success
    dashboard[2](paint=(255, 200, 100))  # Yellow for warning
    dashboard[3](paint=(255, 100, 100))  # Red for error
  
    await dashboard.start()

asyncio.run(status_dashboard())
```

### Example 3: Loading Animation

```python
import asyncio
from textAnimator import TextAnimator, MODES, AnimatorFlags

async def loading_animation():
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
  
    for frame in frames:
        print(f"\r{frame} Loading...", end="", flush=True)
        await asyncio.sleep(0.1)
  
    # Final message
    animator = TextAnimator(
        text="✅ Loading Complete!",
        mode=MODES.TYPEWRITER,
        paint=(100, 255, 100),
        flags=AnimatorFlags.AutoNewline
    )
    await animator.start()

asyncio.run(loading_animation())
```

### Example 4: Runtime Modification Demo

```python
import asyncio
from textAnimator import TextAnimator, MODES

async def runtime_demo():
    animator = TextAnimator(text="Original")
  
    # Start with basic setup
    await asyncio.sleep(1)
  
    # Change while potentially running
    animator(text="Changed!", mode=MODES.MARQUEE, paint=(255, 0, 0))
  
    await asyncio.sleep(1)
  
    # More changes
    animator(mode=MODES.SCRAMBLE, interval=0.02)
  
    await asyncio.sleep(1)
  
    # Final state
    animator(text="Final Result!", mode=MODES.BOUNCE, paint=(0, 255, 0))
  
    await animator.start()

asyncio.run(runtime_demo())
```

---

## 🔧 Advanced Usage

### Custom Animation Mode

```python
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
            wave_text += "∼" if (i + progress * 10) % 2 < 1 else "˙"
  
    return wave_text

# Register the custom mode
register_mode("wave", custom_wave_mode)

# Use it
animator = TextAnimator(text="Wave Animation", mode="wave")
await animator.start()
```

### Complex Color Gradients

```python
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
await animator.start()
```

### Error Handling

```python
try:
    multi = MultiTextAnimator(lines=["A", "B", "C"])
    multi[0](paint=(255, 0, 0))
    multi[1](paint=(0, 255, 0))
    multi[5](paint=(0, 0, 255))  # This will raise IndexError
except IndexError as e:
    print(f"Error: {e}")

# Safe access pattern
if len(multi.__animators__) > 2:
    multi[2](paint=(0, 0, 255))
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas for contribution:

- New animation modes
- Additional color schemes
- Performance improvements
- Documentation enhancements
- Bug fixes

### Development Setup

1. Clone the repository
2. Install development dependencies (if any)
3. Run tests: `python -m pytest`
4. Submit a pull request


**(as this is a one man project your requests may take awhile to be looked at and implemanted)**

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- Built for terminal enthusiasts and CLI developers
- Inspired by ASCII art and retro terminal aesthetics
- Designed for Python 3.7+ with async/await support
- Zero dependencies - pure Python implementation

---

## Support

If you encounter any issues or have questions:

1. Check the examples above
2. Review the API reference
3. Open an issue on GitHub

**Happy animating!**
