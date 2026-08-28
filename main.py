#!/usr/bin/env python3
# main.py — VIOLA Analyzer entry point

from processor  import start_processing_thread, add_message
from simulation import start_simulation
from config     import K_INTERVAL


def main() -> None:
    start_processing_thread(K_INTERVAL)
    print("--- VIOLA ANALYZER ACTIVE (OSC ACTIVE) ---")
    print("Commands: 'simulate' | 'exit' | any text to inject manually\n")

    while True:
        try:
            user_input = input("Command > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[EXIT] Shutting down.")
            break

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("[EXIT] Shutting down.")
            break
        elif user_input.lower() == "simulate":
            start_simulation()
        else:
            add_message(user_input)
            print(f"[QUEUED] '{user_input}' added to buffer.")


if __name__ == "__main__":
    main()
