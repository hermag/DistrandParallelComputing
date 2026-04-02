"""
Barrier — All Threads Wait Until N Have Arrived
================================================
A Barrier blocks each thread that calls barrier.wait() until exactly
N threads have done so, then releases all N simultaneously.

  barrier.wait()  → block until all N threads arrive; returns this
                    thread's position index (0 … N-1)
  barrier.reset() → reset to initial state (no threads must be waiting)
  barrier.abort() → put barrier into broken state, wake all waiters
                    with BrokenBarrierError

Useful for: phased simulations, parallel pipelines where every worker
must finish step K before any begins step K+1.

Demo: A 3-phase scientific simulation.
  Phase 1 — Initialise local data   (variable duration)
  ── BARRIER 1: everyone must finish init before any starts compute ──
  Phase 2 — Run computation          (variable duration)
  ── BARRIER 2: everyone must finish compute before any starts output ──
  Phase 3 — Write output             (fast, uniform)

The timestamps printed show that NO worker ever begins phase K+1 before
ALL workers have completed phase K.
"""

import threading
import time
import random


N_WORKERS = 7

# Two barriers — one per phase boundary
barrier_after_init    = threading.Barrier(N_WORKERS)
barrier_after_compute = threading.Barrier(N_WORKERS)

# Shared log (protected by log_lock)
log_lock = threading.Lock()
timeline: list[tuple[float, str]] = []   # (timestamp, message)
t0 = time.perf_counter()

# Track when each phase completes per worker
phase_done: dict[str, dict[int, float]] = {
    "init":    {},
    "compute": {},
    "output":  {},
}


def log(msg: str) -> None:
    ts = time.perf_counter() - t0
    with log_lock:
        timeline.append((ts, msg))
        print(f"  t={ts:5.3f}s  {msg}")


def simulation_worker(worker_id: int) -> None:
    name = f"Worker-{worker_id}"

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 1 — Initialise
    # ─────────────────────────────────────────────────────────────────────────
    init_sec = random.uniform(0.1, 0.9)
    log(f"{name:10s}  Phase 1 START  (init will take {init_sec:.2f}s)")
    time.sleep(init_sec)
    phase_done["init"][worker_id] = time.perf_counter() - t0
    log(f"{name:10s}  Phase 1 DONE  → arriving at barrier 1 …")

    # ── Barrier 1: wait for ALL workers to finish init ────────────────────────
    try:
        pos = barrier_after_init.wait()
    except threading.BrokenBarrierError:
        log(f"{name:10s}  Barrier 1 BROKEN — aborting")
        return

    if pos == 0:                      # only one thread gets position 0
        log(f"\n  {'─'*46}")
        log(f"  *** Barrier 1 released — ALL {N_WORKERS} workers finished init ***")
        log(f"  {'─'*46}\n")

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 2 — Compute
    # ─────────────────────────────────────────────────────────────────────────
    compute_sec = random.uniform(0.2, 0.8)
    log(f"{name:10s}  Phase 2 START  (compute will take {compute_sec:.2f}s)")
    time.sleep(compute_sec)
    phase_done["compute"][worker_id] = time.perf_counter() - t0
    log(f"{name:10s}  Phase 2 DONE  → arriving at barrier 2 …")

    # ── Barrier 2: wait for ALL workers to finish compute ─────────────────────
    try:
        pos = barrier_after_compute.wait()
    except threading.BrokenBarrierError:
        log(f"{name:10s}  Barrier 2 BROKEN — aborting")
        return

    if pos == 0:
        log(f"\n  {'─'*46}")
        log(f"  *** Barrier 2 released — ALL {N_WORKERS} workers finished compute ***")
        log(f"  {'─'*46}\n")

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 3 — Output
    # ─────────────────────────────────────────────────────────────────────────
    log(f"{name:10s}  Phase 3 START  (writing output)")
    time.sleep(0.05)
    phase_done["output"][worker_id] = time.perf_counter() - t0
    log(f"{name:10s}  Phase 3 DONE  ✓")


def verify_ordering() -> None:
    """
    Prove that every worker's Phase 2 start time is AFTER every worker's
    Phase 1 finish time, and similarly for Phase 3.
    """
    print()
    print("=" * 58)
    print("  VERIFICATION — Phase ordering was respected")
    print("=" * 58)

    last_init    = max(phase_done["init"].values())
    last_compute = max(phase_done["compute"].values())

    print(f"\n  Last worker to finish Phase 1 (init):    t={last_init:.3f}s")
    print(f"  Last worker to finish Phase 2 (compute): t={last_compute:.3f}s")

    # Every compute finish time must be > every init finish time?
    # (we can only guarantee that ALL compute starts are AFTER last init finish)
    # We verify by checking the barrier release point via the timeline.
    barrier1_release = None
    barrier2_release = None
    for ts, msg in timeline:
        if "Barrier 1 released" in msg:
            barrier1_release = ts
        if "Barrier 2 released" in msg:
            barrier2_release = ts

    print(f"\n  Barrier 1 released at: t={barrier1_release:.3f}s")
    print(f"  Barrier 2 released at: t={barrier2_release:.3f}s")

    # All init times must be <= barrier1_release
    for wid, t in phase_done["init"].items():
        assert t <= barrier1_release + 0.01, (
            f"Worker-{wid} finished init AFTER barrier 1 released!"
        )

    # All compute times must be <= barrier2_release
    for wid, t in phase_done["compute"].items():
        assert t <= barrier2_release + 0.01, (
            f"Worker-{wid} finished compute AFTER barrier 2 released!"
        )

    print()
    print("  ✓ All Phase 1 completions were BEFORE Barrier 1 release")
    print("  ✓ All Phase 2 completions were BEFORE Barrier 2 release")
    print("  ✓ No worker skipped ahead — barrier ordering was enforced")
    print()
    print("  Key points:")
    print("    barrier.wait()  — each thread blocks until ALL N arrive")
    print("    position 0      — one designated thread does post-barrier setup")
    print("    Two barriers    — enforce TWO distinct phase boundaries")


if __name__ == "__main__":
    print("=" * 58)
    print(f"  Barrier Demo — 3-phase simulation  ({N_WORKERS} workers)")
    print("=" * 58)
    print()

    workers = [
        threading.Thread(target=simulation_worker, args=(i,),
                         name=f"Worker-{i}")
        for i in range(1, N_WORKERS + 1)
    ]

    for w in workers:
        w.start()

    for w in workers:
        w.join()

    verify_ordering()