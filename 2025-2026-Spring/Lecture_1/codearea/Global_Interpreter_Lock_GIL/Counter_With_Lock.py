import threading

counter = 0
lock = threading.Lock()

def increment_safe():
    global counter
    for _ in range(100000):
        with lock:  # Thread-safe
            counter += 1

threads = [threading.Thread(target=increment_safe) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Counter: {counter}")  # Always: 1,000,000 ✓

# Explanation:
# Here, we use a threading.Lock to ensure that only one thread can modify the counter at
# a time. The with lock: statement acquires the lock before entering the block and releases
# it afterward, preventing race conditions and ensuring thread safety.