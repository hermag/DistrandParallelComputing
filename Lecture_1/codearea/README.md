If we run threads without join.
It will not wait for the thread, strated from another thread to be finished. It will finish it's work and let another thread run, as it is show in Python_Threads_without_join.py file.

If the join is used, the main thread will wait until it's child thread finishes the execution.
