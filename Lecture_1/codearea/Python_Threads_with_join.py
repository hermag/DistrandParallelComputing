import threading
import time

def print_message():
    for i in range(5):
        print("Hello from the thread, triggered from the main thread!")
        time.sleep(1)

# Create a thread that runs the print_message function
def main():
    thread = threading.Thread(target=print_message) # Create thread object, which will run print_message function
    
    # Start the thread
    thread.start()
        
    thread.join()  # Wait for the thread to complete
    
    print("Thre main thread has finished execution.")

if __name__ == "__main__":
    main()