"""
Event — wait(), set(), clear()
==============================
An Event wraps a boolean flag with thread-safe signalling.

  event.wait()      → block until the flag is True
  event.set()       → set flag to True, wake ALL waiting threads
  event.clear()     → reset flag to False (reusable)
  event.is_set()    → non-blocking check

Demo: A multi-lap race simulation.
  • A "ready check" Event makes all runners confirm they are ready before
    the starter fires the gun (event.set()).
  • A "start gun" Event holds all runners at the starting line until fired.
  • A "stop" Event signals runners to finish their current lap and exit.
  • After the race, clear() resets the start gun for a second race round.
"""

import threading
import time
import random


# ── Events ──────────────────────────────────────────────────────────────────
start_gun  = threading.Event()   # runners wait here before the race
stop_flag  = threading.Event()   # set when the race is over

# ── Shared stats (protected by stats_lock) ──────────────────────────────────
stats_lock = threading.Lock()
lap_counts: dict[str, int] = {}
ready_count = 0

N_RUNNERS = 6
RACE_DURATION = 1.2   # seconds before stop signal is sent


def runner(name: str, lap_time_range: tuple[float, float]) -> None:
    """Simulate a runner who waits for the start gun then runs laps."""
    global ready_count

    # ── Ready phase ───────────────────────────────────────────────────────────
    with stats_lock:
        ready_count += 1
        n = ready_count
    print(f"  {name:8s} is on the starting line  [{n}/{N_RUNNERS} ready]")

    # ── Wait for start gun ────────────────────────────────────────────────────
    start_gun.wait()            # ← ALL runners block here until set() fires
    print(f"  {name:8s} ▶ GO!")

    # ── Run laps until stop signal ────────────────────────────────────────────
    laps = 0
    while not stop_flag.is_set():
        lap_sec = random.uniform(*lap_time_range)
        time.sleep(lap_sec)

        if stop_flag.is_set():
            break               # don't count a lap started after stop

        laps += 1
        with stats_lock:
            lap_counts[name] = laps
        print(f"  {name:8s} completed lap {laps}  ({lap_sec:.2f}s)")

    print(f"  {name:8s} ■ finished with {laps} lap(s)")


def race_director() -> None:
    """Controls the start gun and stop flag timing."""
    # Wait until all runners have reached the starting line
    while True:
        with stats_lock:
            if ready_count >= N_RUNNERS:
                break
        time.sleep(0.05)

    print("\n  [Director] All runners ready!")
    time.sleep(0.3)
    print("  [Director] On your marks... Get set...")
    time.sleep(0.4)
    print("  [Director] BANG! → start_gun.set()\n")
    start_gun.set()             # ← wake ALL runners simultaneously

    time.sleep(RACE_DURATION)

    print(f"\n  [Director] Race over! → stop_flag.set()")
    stop_flag.set()             # ← signal all runners to stop after current lap


def print_results() -> None:
    print("\n" + "─" * 42)
    print("  RESULTS")
    print("─" * 42)
    sorted_results = sorted(lap_counts.items(), key=lambda x: -x[1])
    for rank, (name, laps) in enumerate(sorted_results, start=1):
        bar = "▓" * laps
        print(f"  {rank}. {name:8s}  {bar}  {laps} lap(s)")
    print("─" * 42)


if __name__ == "__main__":
    print("=" * 58)
    print("  Event Demo — wait(), set(), clear()")
    print(f"  {N_RUNNERS} runners, race duration: {RACE_DURATION}s")
    print("=" * 58)
    print()

    # Each runner has a different pace
    runner_configs = [
        ("Alice",   (0.20, 0.32)),
        ("Bob",     (0.25, 0.40)),
        ("Carol",   (0.18, 0.28)),
        ("Dave",    (0.30, 0.45)),
        ("Eve",     (0.22, 0.35)),
        ("Frank",   (0.28, 0.50)),
    ]

    threads = [
        threading.Thread(target=runner, args=(name, pace), daemon=True)
        for name, pace in runner_configs
    ]
    director_thread = threading.Thread(target=race_director, daemon=True)

    for t in threads:
        t.start()
    director_thread.start()

    for t in threads:
        t.join()
    director_thread.join()

    print_results()

    # ── Demonstrate clear() — reset for a second round ───────────────────────
    print("\n  [Director] Resetting for round 2 → start_gun.clear()")
    start_gun.clear()
    stop_flag.clear()
    print(f"  start_gun.is_set() = {start_gun.is_set()}   (ready for reuse)")
    print(f"  stop_flag.is_set() = {stop_flag.is_set()}   (ready for reuse)")

    print()
    print("  Key points:")
    print("    wait()  — blocked ALL runners at the starting line simultaneously")
    print("    set()   — released ALL of them at exactly the same moment")
    print("    clear() — reset the event so it can be reused for round 2")