"""
This function is designed to handle a critical section of code that may be accessed by multiple threads simultaneously. 
To ensure thread safety and prevent race conditions, a memory lock is implemented. 

Motivation:
In a multithreaded environment, multiple threads may attempt to read or write shared resources concurrently. 
Without proper synchronization, this can lead to inconsistent or corrupted data. 
The memory lock ensures that only one thread can access the critical section at a time, 
thereby maintaining data integrity and preventing unexpected behavior.
"""
