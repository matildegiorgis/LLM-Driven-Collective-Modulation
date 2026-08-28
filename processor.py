# processor.py — Shared state, buffer, and collective analysis loop

import time
import threading

from config import (
    INITIAL_PARAMS,
    K_INTERVAL,
    RAMP_HIGH_CONF,
    RAMP_LOW_CONF,
    CONFIDENCE_THRESHOLD,
)
from gemini_client import call_gemini
from osc_handler import send_params
from logger import PerformanceLogger

# --- Shared state ---
current_params: dict = INITIAL_PARAMS.copy()

# Each entry: (enqueue_time_s, message_str)
audience_buffer: list[tuple[float, str]] = []

lock = threading.Lock()
perf_logger = PerformanceLogger()


def add_message(text: str) -> None:
    """Thread-safe: append a timestamped message to the audience buffer."""
    with lock:
        audience_buffer.append((time.perf_counter(), text))


def _compute_new_params(current: dict, data: dict) -> dict:
    return {
        "p": max(0.5, min(2.0,
            current["p"] + data["pitch"]["intent"] * data["pitch"]["confidence"] * 0.4)),
        "f": max(0.1, min(20.0,
            current["f"] + data["fragmentation"]["intent"] * data["fragmentation"]["confidence"] * 5.0)),
        "d": max(0.1, min(5.0,
            current["d"] + data["dynamics"]["intent"] * data["dynamics"]["confidence"] * 1.5)),
        "t": max(100.0, min(8000.0,
            current["t"] + data["timbre"]["intent"] * data["timbre"]["confidence"] * 2000.0)),
    }


def processing_loop(k_interval: int = K_INTERVAL) -> None:
    """
    Runs in a background daemon thread.
    Every k_interval seconds it drains the buffer and fires a Gemini analysis.

    Latency metrics tracked per cycle
    -----------------------------------
    api_ms          — Gemini HTTP round-trip
    cycle_ms        — wall time from batch snapshot to OSC send
    avg_msg_wait_ms — average time each message spent in the buffer
    max_msg_wait_ms — worst-case message wait time
    """
    global current_params

    while True:
        time.sleep(k_interval)

        with lock:
            if not audience_buffer:
                print("\n[IDLE] No input to process.")
                continue
            batch = list(audience_buffer)
            audience_buffer.clear()

        cycle_start = time.perf_counter()

        enqueue_times = [ts for ts, _ in batch]
        messages      = [msg for _, msg in batch]

        print(f"\n--- ANALYZING BATCH ({len(messages)} messages) ---")

        # ── Timer A: LLM call start ──────────────────────────────────────────
        llm_start = time.perf_counter()
        data, api_ms = call_gemini(messages, current_params)
        # llm_start marks the exact moment the request left for Gemini

        if data is None:
            print("[SKIP] Gemini returned no data; keeping current state.")
            continue

        # --- Ramp decision ---
        avg_conf = sum(d.get("confidence", 0.5) for d in data.values()) / 4
        ramp_ms  = RAMP_HIGH_CONF if avg_conf > CONFIDENCE_THRESHOLD else RAMP_LOW_CONF

        old_params     = current_params.copy()
        current_params = _compute_new_params(current_params, data)

        # --- Send OSC ---
        send_params(current_params, ramp_ms)

        # ── Timer A: LLM → update complete ──────────────────────────────────
        llm_to_update_ms = (time.perf_counter() - llm_start) * 1000

        cycle_end = time.perf_counter()

        # --- Latency calculations ---
        #
        # max_e2e_ms  = earliest buffered message → OSC send complete
        #               (worst-case a user could experience)
        # llm_to_update_ms = Gemini call start → OSC send complete
        #               (pure system processing latency, no queuing)
        # api_ms      = Gemini HTTP round-trip only
        # cycle_ms    = buffer drain → OSC send (includes pre-LLM overhead)
        #
        wait_times_ms    = [(cycle_end - ts) * 1000 for ts in enqueue_times]
        avg_wait_ms      = sum(wait_times_ms) / len(wait_times_ms)
        max_e2e_ms       = max(wait_times_ms)   # earliest msg → OSC send
        cycle_ms         = (cycle_end - cycle_start) * 1000

        latency = {
            "api_ms":            api_ms,
            "llm_to_update_ms":  llm_to_update_ms,
            "cycle_ms":          cycle_ms,
            "avg_msg_wait_ms":   avg_wait_ms,
            "max_e2e_ms":        max_e2e_ms,
        }

        print(
            f"[LATENCY] API:{api_ms:.0f}ms  "
            f"LLM→Update:{llm_to_update_ms:.0f}ms  "
            f"MaxE2E:{max_e2e_ms:.0f}ms  "
            f"AvgWait:{avg_wait_ms:.0f}ms"
        )

        perf_logger.log_cycle(messages, old_params, current_params, ramp_ms, latency)


def start_processing_thread(k_interval: int = K_INTERVAL) -> threading.Thread:
    t = threading.Thread(target=processing_loop, args=(k_interval,), daemon=True)
    t.start()
    return t
