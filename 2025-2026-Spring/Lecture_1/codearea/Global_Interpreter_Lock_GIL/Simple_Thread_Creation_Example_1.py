import threading
import time

def worker(name, delay):
    print(f"{name} starting")
    time.sleep(delay)
    print(f"{name} finished")

# Create threads
t1 = threading.Thread(target=worker, args=("Thread-1", 2))
t2 = threading.Thread(target=worker, args=("Thread-2", 1))

# Start threads
t1.start()
t2.start()

# Wait for completion
t1.join()
t2.join()

print("All threads completed")