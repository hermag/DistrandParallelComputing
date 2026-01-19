import threading

result = []
lock = threading.Lock()

def calculate_square(numbers):
    for n in numbers:
        with lock:
            result.append(n * n)

# Split work across threads
t1 = threading.Thread(target=calculate_square, args=([1, 2, 3],))
t2 = threading.Thread(target=calculate_square, args=([4, 5, 6],))

t1.start()
t2.start()
t1.join()
t2.join()

print(f"Results: {sorted(result)}")  # [1, 4, 9, 16, 25, 36]