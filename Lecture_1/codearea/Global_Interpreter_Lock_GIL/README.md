**Core Concepts**
***What is Multithreading?***
- Running multiple threads (lightweight processes) concurrently within a single program to improve performance for I/O-bound tasks.
***What is a Race Condition?***
- When multiple threads access shared data simultaneously and the result depends on unpredictable timing. Check Race_Condition_Example.py
***What is a Lock?***
- A synchronization mechanism that ensures only one thread can access protected code at a time.

**Check the Counter_Without_Lock.py file, there is an example of unlocked threads**

# Why Race Conditions Happens in Counter_Without_Lock.py the Detailed Explanation

Why We Lose ~300,000-400,000 Increments
The Root Cause: counter += 1 is NOT Atomic
When you write counter += 1, you think it's one operation. It's actually THREE separate operations:
pythoncounter += 1

**Is actually:**
temp = counter      # Step 1: READ the current value
temp = temp + 1     # Step 2: ADD 1 to it
counter = temp      # Step 3: WRITE back the new value
```

These three steps are **not atomic** - they can be interrupted by other threads.

---

## Visual Step-by-Step Example

Let's see what happens with just **2 threads** and `counter = 0`:

### Scenario 1: Perfect Timing (No Race Condition)
```
Time | Thread 1           | Thread 2           | counter
-----|--------------------|--------------------|--------
  0  |                    |                    | 0
  1  | READ counter (0)   |                    | 0
  2  | ADD 1 (0 + 1 = 1)  |                    | 0
  3  | WRITE counter = 1  |                    | 1
  4  |                    | READ counter (1)   | 1
  5  |                    | ADD 1 (1 + 1 = 2)  | 1
  6  |                    | WRITE counter = 2  | 2
```

**Result: 2 ✓** (Correct! Both increments counted)

---

### Scenario 2: Bad Timing (Race Condition - Lost Update)
```
Time | Thread 1           | Thread 2           | counter
-----|--------------------|--------------------|--------
  0  |                    |                    | 0
  1  | READ counter (0)   |                    | 0
  2  | ADD 1 (0 + 1 = 1)  | READ counter (0)   | 0  ← Both read 0!
  3  |                    | ADD 1 (0 + 1 = 1)  | 0
  4  | WRITE counter = 1  |                    | 1
  5  |                    | WRITE counter = 1  | 1  ← Overwrites!
```

**Result: 1 ❌** (Wrong! We did 2 increments but counter is only 1)

**What happened?**
- Both threads READ the value 0 before either wrote back
- Both calculated 0 + 1 = 1
- Both wrote 1
- One increment was **LOST**

This is called a **"lost update"** - Thread 2's write overwrote Thread 1's work.

---

## Why It Gets Worse with 10 Threads

With 10 threads, the race condition happens **thousands of times**:
```
Thread 1: READ (500) → ADD (501) → ...
Thread 2: READ (500) → ADD (501) → ...  ← Read same value!
Thread 3: READ (500) → ADD (501) → ...  ← Read same value!
Thread 4: READ (500) → ADD (501) → ...  ← Read same value!
...
Thread 1: ... → WRITE (501)
Thread 2: ... → WRITE (501)  ← Overwrites!
Thread 3: ... → WRITE (501)  ← Overwrites!
Thread 4: ... → WRITE (501)  ← Overwrites!
```

If 4 threads all read value 500 before any write back:
- All 4 calculate 501
- All 4 write 501
- **3 increments are lost!** (Should be 504, but we got 501)

---

## Mathematical Analysis

Let's calculate how many updates get lost:

**Setup:**
- 10 threads
- Each does 100,000 increments
- Total expected: 1,000,000

**What actually happens:**

On average, let's say **2-3 threads** collide (read the same value) at any given time.
```
Collision scenario:
- 3 threads read value 1000
- All 3 calculate 1001
- All 3 write 1001
- Result: Only 1 increment counted, 2 lost
- Loss rate: 2/3 = 66% of those operations
```

If this happens frequently throughout execution:
- Best case (minimal collisions): ~900,000 (90% success)
- Typical case: ~700,000 (70% success)
- Worst case (many collisions): ~600,000 (60% success)

**Loss of 300,000-400,000 increments is normal without locks!**

---

## Real Execution Timeline (Simplified)

Here's what might happen with your 10 threads:
```
Microsecond | Thread Actions                        | counter
------------|---------------------------------------|--------
    0       | All 10 threads start                 | 0
    1       | T1: READ(0), T2: READ(0), T3: READ(0)| 0
    2       | T4: READ(0), T5: READ(0)             | 0
    3       | T1: WRITE(1)                         | 1
    4       | T2: WRITE(1) ← overwrites!           | 1
    5       | T3: WRITE(1) ← overwrites!           | 1
    6       | T4: WRITE(1) ← overwrites!           | 1
    7       | T5: WRITE(1) ← overwrites!           | 1
5 threads did increments, but counter only went from 0 to 1!
4 increments were lost!
This pattern repeats thousands of times during execution.

Proof with Detailed Example
Let's trace 10 operations with 2 threads:
python# Thread 1 does 5 increments
# Thread 2 does 5 increments
# Expected final value: 10
```

**Timeline:**
```
Time | T1 Action        | T2 Action        | counter | Notes
-----|------------------|------------------|---------|------------------
  0  |                  |                  | 0       | Initial
  1  | READ(0)          |                  | 0       |
  2  | ADD(1)           | READ(0)          | 0       | T2 reads old value!
  3  | WRITE(1)         | ADD(1)           | 1       |
  4  |                  | WRITE(1)         | 1       | Lost T1's work!
  5  | READ(1)          |                  | 1       |
  6  | ADD(2)           | READ(1)          | 1       |
  7  | WRITE(2)         | ADD(2)           | 2       |
  8  | READ(2)          | WRITE(2)         | 2       | Lost T1's work again!
  9  | ADD(3)           |                  | 2       |
 10  | WRITE(3)         | READ(3)          | 3       |
 11  | READ(3)          | ADD(4)           | 3       |
 12  | ADD(4)           | WRITE(4)         | 4       |
 13  | WRITE(4)         | READ(4)          | 4       | Lost T1's work!
 14  |                  | ADD(5)           | 4       |
 15  | READ(4)          | WRITE(5)         | 5       |
 16  | ADD(5)           |                  | 5       |
 17  | WRITE(5)         |                  | 5       | Lost T2's work!
Expected: 10, Actual: 5
50% of increments were lost! This is exactly what happens in your code.

Why Results Vary Each Run
The race condition depends on thread scheduling which is:

Non-deterministic (unpredictable)
Controlled by the operating system
Affected by CPU load, number of cores, OS scheduler

Run 1: Threads happen to collide less → Result: 850,000
Run 2: More collisions happen → Result: 650,000
Run 3: Different timing → Result: 720,000
It's never the same twice! This makes race conditions incredibly hard to debug.