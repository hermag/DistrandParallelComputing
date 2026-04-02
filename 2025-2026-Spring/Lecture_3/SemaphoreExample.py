"""
Semaphore — Limit Concurrent Access to N Threads
=================================================
A Semaphore maintains an internal counter initialised to N.
  acquire() → counter - 1  (blocks when counter reaches 0)
  release() → counter + 1  (wakes a blocked thread)

Demo: A connection pool that allows at most MAX_CONNECTIONS = 5 threads
to hold an active "database connection" simultaneously.
A live dashboard printed to the terminal proves the limit is never crossed.
"""

import threading
import time
import random
from collections import defaultdict


MAX_CONNECTIONS = 5
TOTAL_WORKERS   = 20

# ── Shared state (all access protected by stats_lock) ──────────────────────
semaphore       = threading.Semaphore(MAX_CONNECTIONS)
stats_lock      = threading.Lock()
active_ids: set[int]    = set()      # which thread IDs are currently connected
peak_concurrent: int    = 0          # highest simultaneous count ever seen
completed: list[int]    = []         # thread IDs that finished
wait_times: dict[int, float]  = {}   # seconds each thread waited for a slot
hold_times: dict[int, float]  = {}   # seconds each thread held the connection


def _snapshot() -> str:
    """Return a one-line dashboard string (called under stats_lock)."""
    bar  = "█" * len(active_ids) + "░" * (MAX_CONNECTIONS - len(active_ids))
    ids  = ",".join(f"{i:02d}" for i in sorted(active_ids)) or "—"
    return (f"  [{bar}] {len(active_ids):d}/{MAX_CONNECTIONS}  "
            f"active=[{ids}]  done={len(completed)}/{TOTAL_WORKERS}")


def database_worker(worker_id: int) -> None:
    global peak_concurrent

    # ── Waiting phase ────────────────────────────────────────────────────────
    t_start_wait = time.perf_counter()
    print(f"  Worker-{worker_id:02d} ▷ waiting for a connection slot...")
    semaphore.acquire()                     # ← blocks until slot is free
    t_acquired = time.perf_counter()
    wait_sec = t_acquired - t_start_wait

    # ── Connected phase ──────────────────────────────────────────────────────
    with stats_lock:
        active_ids.add(worker_id)
        wait_times[worker_id] = wait_sec
        if len(active_ids) > peak_concurrent:
            peak_concurrent = len(active_ids)
        snap = _snapshot()

    print(f"  Worker-{worker_id:02d} ● CONNECTED   (waited {wait_sec:.2f}s)  {snap}")

    # Simulate a query of variable length
    hold_sec = random.uniform(0.3, 1.1)
    time.sleep(hold_sec)

    # ── Release phase ────────────────────────────────────────────────────────
    with stats_lock:
        active_ids.discard(worker_id)
        hold_times[worker_id] = hold_sec
        completed.append(worker_id)
        snap = _snapshot()

    semaphore.release()                     # ← opens slot for next thread
    print(f"  Worker-{worker_id:02d} ○ RELEASED    (held    {hold_sec:.2f}s)  {snap}")


if __name__ == "__main__":
    print("=" * 66)
    print("  Semaphore Demo — max 5 concurrent DB connections")
    print(f"  Workers: {TOTAL_WORKERS}   Limit: {MAX_CONNECTIONS}")
    print("=" * 66)
    print()

    workers = [
        threading.Thread(target=database_worker, args=(i,), name=f"W{i:02d}")
        for i in range(1, TOTAL_WORKERS + 1)
    ]

    t0 = time.perf_counter()
    for w in workers:
        w.start()
        time.sleep(0.02)            # stagger launches slightly for readability

    for w in workers:
        w.join()

    elapsed = time.perf_counter() - t0

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print("=" * 66)
    print(f"  Peak concurrent connections : {peak_concurrent}/{MAX_CONNECTIONS}")
    print(f"  Total wall-clock time       : {elapsed:.2f}s")
    print(f"  Avg wait time per worker    : "
          f"{sum(wait_times.values())/len(wait_times):.2f}s")
    print(f"  Avg hold time per worker    : "
          f"{sum(hold_times.values())/len(hold_times):.2f}s")
    print()

    # ── Correctness assertion ─────────────────────────────────────────────────
    assert peak_concurrent <= MAX_CONNECTIONS, (
        f"VIOLATION: {peak_concurrent} threads connected simultaneously "
        f"(limit is {MAX_CONNECTIONS})!"
    )
    print(f"  ✓ Semaphore limit of {MAX_CONNECTIONS} was NEVER exceeded")
    print()
    print("  Key point: semaphore.acquire() blocks when 5 threads already")
    print("  hold slots. semaphore.release() opens a slot for the next waiter.")