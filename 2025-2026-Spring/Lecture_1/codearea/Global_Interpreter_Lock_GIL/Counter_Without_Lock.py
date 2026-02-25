#Thread UNSAFE CASE
import threading

counter = 0

def increment_unsafe():
    global counter
    for _ in range(100000):
        counter += 1  # Race condition!

threads = [threading.Thread(target=increment_unsafe) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Counter: {counter}")  # Expected: 1,000,000, Actual: ~600,000-900,000