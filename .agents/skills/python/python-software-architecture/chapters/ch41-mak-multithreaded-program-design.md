# Chapter 41: Designing Multithreaded Programs

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 5: Additional Design Techniques (Chapter 16)

## Core Idea
Concurrent programming coordinates multiple execution threads sharing resources; robust design prevents race conditions and deadlocks by synchronizing critical sections with locks and favoring thread-safe communication queues over shared mutable memory.

## Frameworks Introduced
- **The Thread Synchronization Framework**:
  - When to use: When multiple threads access shared mutable data (counters, caches, bank balances).
  - How:
    1. Identify the *Critical Section* (lines of code reading and writing shared state).
    2. Protect the critical section using a `threading.Lock` acquired via Python's context manager (`with lock:`).
    3. Keep critical sections as short as possible to minimize thread contention.
- **Producer-Consumer Architecture via `queue.Queue`**:
  - When to use: Decoupling threads producing tasks from worker threads executing tasks.
  - How: Producers put items onto a thread-safe FIFO `queue.Queue`. Workers pop tasks, execute them, and signal completion via `queue.task_done()`. Eliminates manual locking!

## Key Concepts
- **Race Condition**: A flaw where the system output depends on the non-deterministic sequence or timing of uncontrollable thread scheduling.
- **Critical Section**: A block of code that accesses shared mutable resources and must not be executed concurrently by more than one thread.
- **Deadlock**: A permanent stall occurring when Thread A holds Lock 1 and waits for Lock 2, while Thread B holds Lock 2 and waits for Lock 1.
- **Global Interpreter Lock (GIL)**: Python's internal mutex preventing multiple native threads from executing Python bytecode simultaneously; makes threading ideal for I/O-bound tasks, but requires `multiprocessing` for CPU-bound tasks.

## Mental Models
- **The Single Bathroom Analogy (Locks)**: Multiple people (threads) share a single bathroom (critical section). The lock on the door ensures only one person enters at a time; others wait in the hallway.
- **Conveyor Belt Hand-off (Queues)**: Instead of two workers fighting over the same workbench (shared memory), Worker 1 drops finished parts onto a conveyor belt (Queue), and Worker 2 picks them up.

## Anti-patterns
- **Unprotected Shared Mutations**: Incrementing a shared counter `self.count += 1` across threads without a lock (it is not atomic in Python!).
- **Acquiring Multiple Locks in Inconsistent Order**: Thread 1 acquires Lock A then Lock B; Thread 2 acquires Lock B then Lock A; guarantees eventual deadlock.
- **Using Threading for Heavy CPU Number-Crunching**: Spawning 16 threads for pure matrix multiplication on standard CPython; the GIL forces them onto a single CPU core. Use `multiprocessing` or NumPy instead.

## Code Examples

```python
import threading
import queue
import time

# 1. Protecting Critical Section with Lock
class SafeCounter:
    def __init__(self):
        self._count = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:  # Safe, deterministic acquisition and release
            self._count += 1

    @property
    def value(self) -> int:
        with self._lock:
            return self._count

# 2. Producer-Consumer using Thread-Safe Queue
def producer(q: queue.Queue):
    for i in range(5):
        time.sleep(0.01)
        q.put(f"Task-{i}")
    q.put(None)  # Poison pill to signal termination

def consumer(q: queue.Queue):
    while True:
        task = q.get()
        if task is None:
            break
        print(f"Processed {task}")
        q.task_done()
```
- **What it demonstrates**: Synchronization of shared state using a context-managed Lock, and lock-free coordination via a thread-safe FIFO Queue.

## Reference Tables

| Concurrency Model | Best For | GIL Impact | Synchronization Tool |
|---|---|---|---|
| **Threading (`threading`)** | I/O-bound (web requests, disk) | Bound to 1 core for bytecode | `threading.Lock`, `Queue` |
| **Multiprocessing (`multiprocessing`)**| CPU-bound (math, image processing)| Bypasses GIL; uses all cores | IPC, Pipes, SharedMemory |
| **Asyncio (`asyncio`)** | Massive I/O concurrency (websockets)| Single thread, event loop | `asyncio.Lock`, Coroutines |

## Worked Example
Preventing deadlocks with strict lock ordering:
- *Scenario*: Transferring money between two accounts concurrently.
- *Danger*: If Transfer 1 locks Account A then Account B, while Transfer 2 locks Account B then Account A, deadlock occurs!
- *Deadlock Prevention Rule*: Always acquire locks in a globally consistent order (e.g. by sorting account IDs):
```python
def safe_transfer(source_account, target_account, amount):
    # Sort accounts by unique ID to enforce identical locking order everywhere!
    first, second = sorted([source_account, target_account], key=lambda a: a.id)
    with first.lock:
        with second.lock:
            source_account.withdraw(amount)
            target_account.deposit(amount)
```
No deadlock is possible regardless of thread scheduling.

## Key Takeaways
1. Protect all shared mutable state using `with lock:` context managers.
2. Prefer thread-safe queues (`queue.Queue`) over shared memory whenever possible.
3. Understand the GIL: use `threading` for I/O-bound tasks and `multiprocessing` for CPU-bound tasks.
4. Prevent deadlocks by always acquiring multiple locks in a globally consistent order.

## Connects To
- **Ch 7**: Concurrency control and aggregate boundaries.
- **Ch 8**: Message bus asynchronous event dispatch.
- **Ch 37**: Observer pattern in multithreaded environments.
