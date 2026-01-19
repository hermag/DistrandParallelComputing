If we run threads without join, the main thread will not wait for the triggered threads to be finished. It will finish it's work and let another thread run, as it is show in Python_Threads_without_join.py file. Run it and try to understand the output. 

If the join is used, the main thread will wait until it's child thread finishes the execution.

This program shows how Python can run several threads concurrently, allowing multiple tasks to progress at the same time instead of running sequentially.
Each thread executes the same function (print_numbers) but with different arguments, so they behave independently. 
# Launching Multiple Threads in Python

This example demonstrates how to **launch multiple threads concurrently** using Python’s built-in `threading` module and how the main thread waits for all worker threads to finish.

---

## 📌 Example Code

```python
import threading
import time

def print_numbers(name, count):
    for i in range(count):
        print(f"Thread {name} says {i}")
        time.sleep(1)

def main():
    threads = []
    for i in range(3):
        thread = threading.Thread(
            target=print_numbers,
            args=(f"Thread-{i+1}", 5)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # Wait for all threads to complete

    print("Message from the main thread: All threads have finished execution.")

if __name__ == "__main__":
    main()
```

🧵 How Multiple Threads Are Launched

1️⃣ **Define the task for each thread**

Each thread runs the same function, print_numbers, but receives different arguments.

```python
def print_numbers(name, count):
    for i in range(count):
        print(f"Thread {name} says {i}")
        time.sleep(1)
```
- Prints the thread name and a counter value
- time.sleep(1) simulates work and allows context switching

2️⃣ **Create and start threads in a loop**

Threads are created and started almost simultaneously.

```python
threads = []
for i in range(3):
    thread = threading.Thread(
        target=print_numbers,
        args=(f"Thread-{i+1}", 5)
    )
    threads.append(thread)
    thread.start()
```
- The loop runs three times
- thread.start() launches each thread immediately
- Threads begin executing concurrently

3️⃣ **Threads run concurrently**

Once started, all threads run independently.
Their output is interleaved because the operating system schedules execution time among them.

4️⃣ **Wait for all threads to finish**

The main thread waits for each worker thread to complete.
```python
for thread in threads:
    thread.join()
```
- join() blocks the main thread until a worker thread finishes
- Ensures the program does not exit early

5️⃣ **Resume execution in the main thread**

After all threads have finished, the main thread prints a final message.
```python
print("Message from the main thread: All threads have finished execution.")
```

🖥️ **Sample Output**

```bash
Thread Thread-1 says 0
Thread Thread-2 says 0
Thread Thread-3 says 0
Thread Thread-1 says 1
Thread Thread-2 says 1
Thread Thread-3 says 1
Thread Thread-1 says 2
Thread Thread-2 says 2
Thread Thread-3 says 2
Thread Thread-1 says 3
Thread Thread-2 says 3
Thread Thread-3 says 3
Thread Thread-1 says 4
Thread Thread-2 says 4
Thread Thread-3 says 4
Message from the main thread: All threads have finished execution.
```

✅ **Key Takeaways**
- Threads are launched inside a loop using thread.start()
- All threads begin execution almost at the same time
- The main thread waits for completion using join()
- Output order is not guaranteed
- This pattern is ideal for I/O-bound or waiting tasks

📘 **Notes**
- Threads share the same memory space
- Use synchronization tools (locks, queues) when sharing data
- For CPU-bound tasks, consider multiprocessing instead

