import threading
import time

def print_message(name, count):
    for i in range(count):
        print(f"Hello from the child {name}, number {i}")
        time.sleep(1)

# Create a thread that runs the print_message function
def main():
    thread = threading.Thread(target=print_message, args=("Thread",5)) # passed two arguments, the name of the thread and the number of the threads. 
    # Start the thread
    thread.start()
        
    thread.join()  # Wait for the thread to complete
    
    print("Thre main thread has finished execution.")

if __name__ == "__main__":
    main()