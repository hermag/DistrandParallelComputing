import threading
import time
import random
import sys
import os

NUM_PHILOSOPHERS = 5
NAMES = ["Aristotle", "Plato", "Socrates", "Kant", "Nietzsche"]
SHORT = ["Aristotle", "Plato   ", "Socrates", "Kant    ", "Nietzsche"]

# Terminal column width per philosopher
COL_WIDTH = 18

# Lock for printing (so lines don't interleave)
print_lock = threading.Lock()

# The forks (one between each pair of philosophers)
forks = [threading.Lock() for _ in range(NUM_PHILOSOPHERS)]
print("================>>", forks)

# Track state of each philosopher for the display
states = ["thinking"] * NUM_PHILOSOPHERS
state_lock = threading.Lock()

def clear_and_draw():
    """Redraw the full status table."""
    # Move cursor up to overwrite previous table (header + separator + N rows + separator)
    lines = NUM_PHILOSOPHERS + 3
    sys.stdout.write(f"\033[{lines}A\033[J")

    # Header
    header = ""
    for name in SHORT:
        header += f"{name:<{COL_WIDTH}}"
    print(header)
    print("-" * (COL_WIDTH * NUM_PHILOSOPHERS))

    # State rows
    row = ""
    for i, state in enumerate(states):
        if state == "eating":
            cell = f"\033[92m{'● EATING':<{COL_WIDTH}}\033[0m"
        elif state == "waiting":
            cell = f"\033[93m{'◌ WAITING':<{COL_WIDTH}}\033[0m"
        elif state == "thinking":
            cell = f"\033[94m{'~ thinking':<{COL_WIDTH}}\033[0m"
        elif state.startswith("got fork"):
            cell = f"\033[96m{state:<{COL_WIDTH}}\033[0m"
        else:
            cell = f"{state:<{COL_WIDTH}}"
        row += cell
    print(row)

    # Event log separator
    print("-" * (COL_WIDTH * NUM_PHILOSOPHERS))
    sys.stdout.flush()

def set_state(idx, new_state):
    with state_lock:
        states[idx] = new_state
    #with print_lock:
    #    clear_and_draw()

def log_event(idx, message):
    """Print an event line below the table, then redraw."""
    name = SHORT[idx].strip()
    col_offset = " " * (COL_WIDTH * idx)
    with print_lock:
        # Print event below table
        prefix = " " * (COL_WIDTH * idx)
        print(f"{prefix}\033[90m[{name}] {message}\033[0m")
        sys.stdout.flush()

def philosopher(idx):
    left = idx
    right = (idx + 1) % NUM_PHILOSOPHERS
    name = NAMES[idx]

    for _ in range(4):  # each philosopher eats 4 times
        # THINKING
        set_state(idx, "~ thinking")
        log_event(idx, "thinking...")
        time.sleep(random.uniform(5.5, 6.5))

        # TRY TO PICK UP LEFT FORK
        set_state(idx, "waiting")
        log_event(idx, f"wants fork {left} (left) ← trying acquire")

        acquired_left = False
        while not acquired_left:
            acquired_left = forks[left].acquire(blocking=False)
            if not acquired_left:
                log_event(idx, f"fork {left} busy ← BLOCKED waiting")
                time.sleep(5.2)

        log_event(idx, f"got fork {left} ✓")
        set_state(idx, f"got L fork")

        # TRY TO PICK UP RIGHT FORK
        log_event(idx, f"wants fork {right} (right) ← trying acquire")
        acquired_right = False
        while not acquired_right:
            acquired_right = forks[right].acquire(blocking=False)
            if not acquired_right:
                log_event(idx, f"fork {right} busy ← BLOCKED waiting")
                time.sleep(5.2)

        log_event(idx, f"got fork {right} ✓")

        # EATING
        set_state(idx, "eating")
        log_event(idx, f"*** EATING ***")
        time.sleep(random.uniform(5.8, 5.5))

        # PUT DOWN FORKS
        forks[left].release()
        forks[right].release()
        log_event(idx, f"released forks {left} & {right} → OS wakes waiters")
        set_state(idx, "~ thinking")

    set_state(idx, "done ✓")
    log_event(idx, "finished all meals")


def main():
    # Print initial blank table so clear_and_draw has lines to overwrite
    header = ""
    for name in SHORT:
        header += f"{name:<{COL_WIDTH}}"
    print(header)
    print("-" * (COL_WIDTH * NUM_PHILOSOPHERS))
    print(" " * (COL_WIDTH * NUM_PHILOSOPHERS))  # state row placeholder
    print("-" * (COL_WIDTH * NUM_PHILOSOPHERS))
    sys.stdout.flush()

    threads = []
    for i in range(NUM_PHILOSOPHERS):
        t = threading.Thread(target=philosopher, args=(i,), daemon=True)
        threads.append(t)

    # Stagger starts slightly to make it more interesting
    for i, t in enumerate(threads):
        t.start()
        time.sleep(5.1)

    for t in threads:
        t.join()

    print("\n\033[92mAll philosophers have finished dining.\033[0m")


if __name__ == "__main__":
    main()