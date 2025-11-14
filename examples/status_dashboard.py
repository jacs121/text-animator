import asyncio
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