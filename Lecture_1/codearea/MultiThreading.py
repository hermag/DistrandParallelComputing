import threading
import time

def print_numbers(name, count):
    for i in range(count):
        print(f"Thread {name} says {i}")
        time.sleep(1)

def main():
    threads = []
    for i in range(3):
        thread = threading.Thread(target=print_numbers, args=(f"Thread-{i+1}", 5))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # Wait for all threads to complete
    print("Message from the main thread: All threads have finished execution.") 

if __name__ == "__main__":
    main()   