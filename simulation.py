# simulation.py — Random audience simulation with latency tracking
#
# Messages from all scenario groups are distributed randomly across
# the full simulation duration (default 10 min), exactly as in the
# original design.
#
# Latency is tracked automatically: add_message() stamps each message
# with time.perf_counter() on entry. processor.py computes per-cycle
# avg/max wait times when the batch is drained.

import time
import random
import threading

from config import K_INTERVAL
from processor import add_message

# ---------------------------------------------------------------------------
# All scenario messages, grouped by theme (order within groups is preserved,
# but messages are scattered randomly across the full timeline).
# ---------------------------------------------------------------------------
SCENARIO_POOL: list[list[str]] = [
    [
        "I want the sound darker and deeper",
        "Make it more low and heavy",
        "More bass, less brightness",
        "A calm and slow atmosphere",
    ],
    [
        "I want a moment of building tension",
        "Increase the intensity gradually",
        "Make it more energetic",
    ],
    [
        "Create a frantic energy that keeps accelerating",
        "More movement, more energy",
        "Push the intensity higher",
        "Make it more aggressive",
    ],
    [
        "Make it brighter and sharper",
        "I want it darker and more muffled",
        "Too bright, bring it down",
        "Increase the brightness",
    ],
    [
        "Break the sound into tiny pieces",
        "Make it granular like sand",
        "I want a smooth continuous flow",
        "Remove the fragmentation",
    ],
    [
        "It's too intense, calm it down",
        "Reduce the energy",
        "Make it slower and more stable",
        "Let it breathe slowly",
    ],
    [
        "I want a smooth, liquid atmosphere",
        "Make it soft and continuous",
        "More ambient and less aggressive",
    ],
    [
        "I want an abrupt jump in intensity right now",
        "Sudden change!",
        "Make it explode now",
    ],
    [
        "I want a suffocatingly dense atmosphere",
        "Make it very full and immersive",
        "Thick texture, no space",
    ],
]

# Total simulation duration in seconds
SIMULATION_DURATION = 600  # 10 minutes


def run_timed_simulation(total_duration: int = SIMULATION_DURATION) -> None:
    """
    Scatter all messages randomly across [5s, total_duration - 60s],
    then seed them in chronological order.

    Latency per message = time between add_message() call and the moment
    processor.py drains the buffer. Reported as avg_msg_wait_ms and
    max_msg_wait_ms in the performance log.
    """
    start_time = time.time()
    print(f"\n[SIMULATION] {total_duration // 60}-minute random simulation started.")

    # Assign a random timestamp to every message across all groups
    scheduled: list[tuple[float, str]] = []
    for group in SCENARIO_POOL:
        for msg in group:
            t = random.uniform(5, total_duration - 60)
            scheduled.append((t, msg))

    # Sort so we sleep in order rather than jumping around
    scheduled.sort(key=lambda x: x[0])

    for scheduled_time, msg in scheduled:
        elapsed   = time.time() - start_time
        wait_time = scheduled_time - elapsed
        if wait_time > 0:
            time.sleep(wait_time)

        add_message(msg)   # ← timestamps the message for latency tracking
        print(f"[INPUT SEEDED | t={time.time() - start_time:.1f}s] {msg}")

    print("[SIMULATION] All messages seeded.")


def start_simulation(total_duration: int = SIMULATION_DURATION) -> threading.Thread:
    t = threading.Thread(
        target=run_timed_simulation, args=(total_duration,), daemon=True
    )
    t.start()
    return t
