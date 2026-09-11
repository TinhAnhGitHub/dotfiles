# Chapter 35: The Adapter and Façade Design Patterns

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 4: Design Patterns (Chapter 10)

## Core Idea
Structural boundary patterns reconcile incompatible interfaces: Adapter converts the interface of an existing class into another interface clients expect, while Façade provides a simplified, higher-level interface to an entire complex subsystem.

## Frameworks Introduced
- **The Adapter Pattern (Structural)**:
  - When to use: When you want to use an existing class or third-party library whose interface does not match the contract required by your system.
  - How:
    1. Define the target interface required by your application (Client Interface).
    2. Create an Adapter class that implements the target interface.
    3. Inside the adapter, wrap the existing class (Adaptee) and translate method calls and parameters.
- **The Façade Pattern (Structural)**:
  - When to use: When a subsystem consists of numerous intricate classes and configurations, and clients need a clean, unified entry point.
  - How: Create a single class (`SubsystemFacade`) exposing 2–3 high-level methods that orchestrate calls across the underlying subsystem classes.

## Key Concepts
- **Adaptee**: The existing, incompatible class or service.
- **Adapter**: The wrapper that bridges the gap between client expectations and the adaptee.
- **Façade**: A high-level unified interface hiding the complexity of a multi-class subsystem.
- **Interface Mismatch**: When two components agree on functionality but disagree on method names, signatures, or data formats.

## Mental Models
- **Adapter as a Travel Plug Converter**: When you travel to Europe, your US laptop charger cannot plug into the wall socket. The adapter doesn't change how your laptop works or how the city generates electricity; it translates the physical pins.
- **Façade as a Hotel Concierge**: You tell the concierge: *"I need dinner reservations for four and a taxi."* The concierge calls the restaurant, coordinates with the taxi company, and handles billing. You don't interact with 5 different service workers.

## Anti-patterns
- **Modifying Third-Party Code Directly**: Editing vendor libraries or generated SDK files to match your interface instead of writing an adapter.
- **The God Façade**: Creating a façade that attempts to expose every single granular option of the underlying subsystem, defeating the purpose of simplification.
- **Adapters with Business Logic**: Stuffing domain business calculations inside an adapter; adapters must strictly translate calls, not invent rules.

## Code Examples

```python
# 1. ADAPTER PATTERN
# Target Interface expected by our clean application:
class PaymentProcessor(Protocol):
    def pay(self, amount: float) -> bool: ...

# Incompatible Third-Party Library (Adaptee):
class StripeService:
    def make_charge(self, cents: int, currency: str) -> dict:
        return {"status": "succeeded", "charge_id": "ch_123"}

# Adapter: Translates dollars to cents and method names
class StripeAdapter(PaymentProcessor):
    def __init__(self, stripe_service: StripeService):
        self._service = stripe_service

    def pay(self, amount: float) -> bool:
        cents = int(amount * 100)
        res = self._service.make_charge(cents, currency="usd")
        return res.get("status") == "succeeded"

# 2. FAÇADE PATTERN
# Complex Subsystem:
class AudioCodec: def decode(self, stream): return "audio"
class VideoCodec: def decode(self, stream): return "video"
class BufferManager: def allocate(self): pass
class ScreenRenderer: def draw(self, video, audio): print("Playing movie!")

# Unified Façade:
class VideoPlayerFacade:
    def __init__(self):
        self._audio = AudioCodec()
        self._video = VideoCodec()
        self._buffer = BufferManager()
        self._screen = ScreenRenderer()

    def play_movie(self, filename: str) -> None:
        self._buffer.allocate()
        a = self._audio.decode(filename)
        v = self._video.decode(filename)
        self._screen.draw(v, a)
```
- **What it demonstrates**: Adapter converting third-party Stripe API to a clean application protocol, and Façade encapsulating a multi-stage multimedia decoding subsystem.

## Reference Tables

| Aspect | Adapter Pattern | Façade Pattern |
|---|---|---|
| **Intent** | Convert an incompatible interface | Simplify an entire complex subsystem |
| **Existing Interface** | Replaces/maps an existing interface | Provides a new, higher-level interface |
| **Wrapping Scope** | Typically wraps 1 object (Adaptee) | Wraps multiple subsystem objects |
| **Client Perspective** | Conforms to an existing client interface | Offers convenient shortcut methods |

## Worked Example
Wrapping legacy boto3 S3 calls in a clean storage adapter:
Instead of spraying `boto3.client('s3').put_object(Bucket=..., Key=..., Body=...)` throughout the app:
1. Define Port: `StoragePort` with `upload(path, data: bytes) -> str`.
2. Build Adapter: `S3StorageAdapter(StoragePort)`.
3. In tests, swap `S3StorageAdapter` for `InMemoryStorageAdapter`.

## Key Takeaways
1. Use Adapter to reconcile interface differences without modifying existing classes.
2. Use Façade to provide a clean, high-level interface to a noisy subsystem.
3. Keep adapters strictly focused on translation; do not embed business rules.
4. Both patterns protect core application code from volatile external APIs.

## Connects To
- **Ch 2**: Percival's Repository is an adapter over database queries.
- **Ch 19**: Interface Adapters in Clean Architecture.
- **Ch 24**: Anti-Corruption Layers built using Adapters and Façades.
