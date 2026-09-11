# Chapter 37: The Observer Design Pattern

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 4: Design Patterns (Chapter 12)

## Core Idea
The Observer pattern establishes a one-to-many dependency between objects so that when one object (the Subject) changes state, all its registered dependents (Observers) are notified and updated automatically.

## Frameworks Introduced
- **The Observer / Pub-Sub Framework**:
  - When to use: When changes in one object require updates across an unknown or dynamic number of collaborating objects.
  - How:
    1. Define an `Observer` interface with an `update(*args, **kwargs)` method.
    2. The `Subject` maintains a list or set of registered observers (`attach(observer)`, `detach(observer)`).
    3. When state changes, the subject iterates through its observers and calls `notify()`.
- **Push vs. Pull Notification Models**:
  - When to use: Designing the payload sent to observers.
  - How:
    - **Push Model**: The subject passes complete detail data as arguments in the `update(data)` call. Observers are decoupled from subject methods, but payload schemas are fixed.
    - **Pull Model**: The subject passes only a reference to itself: `update(self)`. Observers query the subject for the specific state attributes they require.

## Key Concepts
- **Subject (Observable)**: The publisher object that maintains observer subscriptions and broadcasts events.
- **Observer (Subscriber)**: The interface or object that reacts to updates from the subject.
- **Loose Coupling in Notifications**: The subject knows only that an observer implements the `Observer` interface; it knows nothing of concrete subscriber implementations.
- **Event-Driven Decoupling**: Eliminating hardcoded cross-component method calls in favor of broadcast notifications.

## Mental Models
- **Newspaper Subscription**: The newspaper printing press (Subject) does not know who reads the paper or what they do with it. Subscribers (Observers) sign up to receive the paper and read the sections they care about.
- **Don't Poll; React**: Instead of 10 worker threads constantly asking "Are you done yet?", the master process notifies them when the task finishes.

## Anti-patterns
- **Lapsed Listener (Memory Leak)**: Registering an observer and forgetting to detach it; the subject retains a reference, preventing garbage collection.
- **Cascading Notification Storms**: Observer A updates Subject B upon notification, which notifies Observer C, which updates Subject A, triggering an infinite event cycle.
- **Tight Coupling via Pull**: Observers reaching into concrete private attributes of the Subject during a pull notification.

## Code Examples

```python
from typing import Protocol, List

# 1. Observer Interface
class WeatherObserver(Protocol):
    def update(self, temperature: float, humidity: float) -> None: ...

# 2. Subject (Observable)
class WeatherStation:
    def __init__(self):
        self._observers: List[WeatherObserver] = []
        self._temperature: float = 0.0
        self._humidity: float = 0.0

    def attach(self, observer: WeatherObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: WeatherObserver) -> None:
        self._observers.remove(observer)

    def set_measurements(self, temp: float, humidity: float) -> None:
        self._temperature = temp
        self._humidity = humidity
        self._notify()

    def _notify(self) -> None:
        for observer in self._observers:
            observer.update(self._temperature, self._humidity)

# 3. Concrete Observers
class PhoneDisplay:
    def update(self, temp: float, humidity: float) -> None:
        print(f"[Phone Display] Temp: {temp}°C, Humidity: {humidity}%")

class AlertSystem:
    def update(self, temp: float, humidity: float) -> None:
        if temp > 38.0:
            print("[ALERT] Extreme heat warning!")
```
- **What it demonstrates**: Pure Push-model Observer pattern decoupling the `WeatherStation` from individual display and alerting systems.

## Reference Tables

| Aspect | Push Model | Pull Model |
|---|---|---|
| **Data Flow** | Subject sends complete data with update | Subject notifies; Observer fetches state |
| **Coupling** | Subject coupled to event data contract | Observer coupled to Subject getter methods |
| **Efficiency** | Sends data observers might not need | Observers fetch only the data they need |
| **Subscribers** | Observers remain completely generic | Observers must know the Subject type |

## Worked Example
Using Python `weakref` to prevent the Lapsed Listener memory leak:

```python
import weakref

class WeakSubject:
    def __init__(self):
        self._observers = weakref.WeakSet()

    def attach(self, observer):
        self._observers.add(observer)

    def notify(self, event):
        for observer in self._observers:
            observer.update(event)
```
When an observer is discarded elsewhere in the program, it is automatically removed from `_observers`, eliminating memory leaks!

## Key Takeaways
1. Observer pattern decouples state holders (subjects) from state consumers (observers).
2. Prefer the Push model for loose coupling across module boundaries.
3. Use `weakref.WeakSet()` to prevent subscription-induced memory leaks.
4. Beware of cascading updates that can produce infinite notification loops.

## Connects To
- **Ch 8**: Percival's domain events and message bus in relation to the GoF Observer pattern.
- **Ch 12**: CQRS view synchronization via event observers.
- **Ch 38**: Combining State pattern transitions with Observer notifications.
