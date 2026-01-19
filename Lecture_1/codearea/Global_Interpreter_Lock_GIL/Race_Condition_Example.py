# Race Condition Example
counter = 0

def increment():  # NOT thread-safe
    global counter
    counter += 1  # Actually 3 operations: read, add, write

# 10 threads doing this = unpredictable results!