import threading
import time

# Simple function that will run in a thread
def say_hello(thread_number):
    print(f"Hello from thread {thread_number}!")
    time.sleep(1)  # Simulate some work
    print(f"Thread {thread_number} finished!")

# Create and start multiple threads
threads = []

for i in range(5):
    thread = threading.Thread(target=say_hello, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

print("All threads completed!")
