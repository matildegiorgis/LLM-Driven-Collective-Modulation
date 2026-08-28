# logger.py — Performance & latency report writer

import datetime


class PerformanceLogger:
    """Appends structured analysis cycles (with latency metrics) to a text file."""

    def __init__(self, filename: str = "performance_report.txt"):
        self.filename = filename
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*70}\n")
            f.write(
                f"OFFLINE ANALYSIS SESSION: "
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"{'='*70}\n")

    def log_cycle(
        self,
        messages: list[str],
        old_p: dict,
        new_p: dict,
        ramp: int,
        latency: dict,
    ) -> None:
        """
        Parameters
        ----------
        messages : list of raw audience strings
        old_p    : previous parameter dict
        new_p    : updated parameter dict
        ramp     : ramp time in ms
        latency  : dict with keys:
                     - api_ms           : Gemini HTTP round-trip (ms)
                     - llm_to_update_ms : Gemini call start → OSC send complete (ms)
                     - cycle_ms         : buffer drain → OSC send complete (ms)
                     - avg_msg_wait_ms  : average time messages spent in buffer (ms)
                     - max_e2e_ms       : earliest buffered message → OSC send (ms)
        """
        ts = datetime.datetime.now().strftime("%H:%M:%S")

        lines = [
            f"[{ts}] ANALYSIS CYCLE",
            f"   AUDIENCE INPUTS ({len(messages)}): {' | '.join(messages)}",
            f"   OLD STATE  -> P:{old_p['p']:.2f}  F:{old_p['f']:.1f}  "
            f"D:{old_p['d']:.1f}  T:{old_p['t']:.0f}",
            f"   NEW STATE  -> P:{new_p['p']:.2f}  F:{new_p['f']:.1f}  "
            f"D:{new_p['d']:.1f}  T:{new_p['t']:.0f}",
            f"   CALC RAMP  : {ramp} ms",
            "   LATENCY BREAKDOWN:",
            f"     • Gemini API call       : {latency['api_ms']:.1f} ms",
            f"     • LLM → Update (KEY)    : {latency['llm_to_update_ms']:.1f} ms",
            f"     • Full cycle time       : {latency['cycle_ms']:.1f} ms",
            f"     • Avg msg buffer wait   : {latency['avg_msg_wait_ms']:.1f} ms",
            f"     • Max end-to-end (worst): {latency['max_e2e_ms']:.1f} ms",
            "-" * 70,
        ]

        report_text = "\n".join(lines) + "\n"
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(report_text)

        print(f"[REPORT] Cycle logged → {self.filename}")
