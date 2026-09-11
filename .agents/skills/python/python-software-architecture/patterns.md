# Software Design Patterns & Architecture Catalog

A structured catalog of tactical patterns across Domain-Driven Design, Clean Architecture, and Gang of Four (GoF) implemented in modern Python.

## 1. Tactical DDD Patterns

### Aggregate & Aggregate Root
- **When to use**: When business invariants span multiple related entities and must be protected against concurrent modification race conditions.
- **How**: Designate an Aggregate Root entity. Route all mutations to child entities exclusively through methods on the root. Lock or version the root upon commit.
- **Trade-offs**: Strong consistency within the aggregate boundary; cross-aggregate operations must rely on eventual consistency via domain events.

### Repository Pattern
- **When to use**: Decoupling domain entities from database persistence frameworks (SQLAlchemy, Django ORM, MongoDB).
- **How**: Declare an `AbstractRepository(Protocol)` with `add(entity)` and `get(id)`. Build a concrete ORM adapter and an in-memory `FakeRepository` for unit tests.
- **Trade-offs**: Adds an abstraction layer over ORMs; simplifies unit testing and database portability.

### Unit of Work (UoW) Pattern
- **When to use**: Maintaining atomic transaction boundaries across multiple repositories during a use case.
- **How**: Implement Python's context manager protocol (`__enter__`, `__exit__`). Roll back on unhandled exceptions; commit explicitly with `uow.commit()`.
- **Trade-offs**: Encapsulates database sessions cleanly; requires passing the UoW through service or handler layers.

---

## 2. Clean Architecture Patterns

### Use Case Interactor
- **When to use**: Encapsulating discrete application workflows independently of HTTP frameworks, CLI tools, or UI delivery mechanisms.
- **How**: Interactor accepts a `RequestDTO`, coordinates Domain Entities and Output Ports, and returns a `ResponseDTO`.
- **Trade-offs**: Prevents fat controllers and anemic domain models; introduces DTO mapping overhead.

### Presenter & ViewModel
- **When to use**: Formatting use case responses for specific client interfaces (HTML, REST, Mobile, CLI) without polluting core interactors.
- **How**: Presenter implements an output boundary, translating a `ResponseDTO` into a UI-ready `ViewModel` (formatted dates, currency strings).
- **Trade-offs**: Keeps controllers thin and templates dumb; requires maintaining separate view data structures.

### Anti-Corruption Layer (ACL)
- **When to use**: Integrating legacy databases or third-party APIs without letting messy external schemas infect clean domain models.
- **How**: Place an adapter between external schemas and domain interfaces that sanitizes and translates incoming data into pristine domain entities.
- **Trade-offs**: Extra translation code; protects the domain model from foreign schema drift and rot.

---

## 3. Behavioral Patterns (GoF)

### Strategy Pattern
- **When to use**: When algorithms must be interchangeable at runtime, or to eliminate sprawling `if/elif` type checks.
- **How**: Define a `Protocol` or accept a Python `Callable`. Inject the chosen strategy function into the context class.
- **Trade-offs**: Greatly increases flexibility and testability; callers must know which strategy to configure.

### State Pattern
- **When to use**: When an object's behavior changes dynamically based on internal state, eliminating nested conditional state checks.
- **How**: Create a polymorphic `State` class hierarchy. The `Context` delegates state-dependent actions to `self._state.action(self)`.
- **Trade-offs**: Makes state transitions explicit and OCP-compliant; increases total number of classes.

### Observer Pattern
- **When to use**: Establishing 1-to-many event notifications where a Subject notifies registered Observers without tight coupling.
- **How**: Subject maintains a list (or `WeakSet`) of subscriber callables and iterates over them in `notify()`.
- **Trade-offs**: Loose coupling between publishers and subscribers; potential memory leaks if observers are not detached.

### Template Method
- **When to use**: Invariant multi-step algorithm workflow where individual steps vary across subclasses.
- **How**: Base class implements the template method calling abstract or hook methods overridden by subclasses.
- **Trade-offs**: Easy code reuse via inheritance; tightly couples subclasses to the base class execution flow.

### Visitor Pattern
- **When to use**: Executing operations across a composite tree (e.g. AST) without polluting node classes with operation methods.
- **How**: Nodes accept a visitor (`node.accept(visitor)`), which double-dispatches back to `visitor.visit_<node>(self)`.
- **Trade-offs**: Trivial to add new operations; very difficult to add new node types to the tree structure.

---

## 4. Structural Patterns (GoF)

### Adapter Pattern
- **When to use**: Reconciling incompatible interfaces between two classes or third-party libraries.
- **How**: Wrap the adaptee class inside an adapter implementing the interface expected by the client.
- **Trade-offs**: Bridges legacy/vendor code seamlessly; slight indirection overhead.

### Façade Pattern
- **When to use**: Providing a simplified, high-level interface to a complex multi-class subsystem.
- **How**: Create a unified wrapper class exposing 2–3 coarse-grained methods that orchestrate underlying subsystem classes.
- **Trade-offs**: Shields clients from complex wiring; can risk becoming a God Class if too many features are added.

### Composite Pattern
- **When to use**: Treating individual objects (leaves) and compositions of objects (branches) uniformly in tree hierarchies.
- **How**: Leaves and Containers implement a common Component interface; Containers delegate operations recursively to children.
- **Trade-offs**: Simplifies client traversal; makes type-specific constraints harder to enforce at compile time.

### Decorator Pattern
- **When to use**: Dynamically augmenting an object's behavior (logging, caching, encryption) without class inheritance.
- **How**: Decorator implements the Component interface, wraps a Component instance, and wraps calls with extra behavior.
- **Trade-offs**: Highly composable at runtime; deep decorator chains can complicate stack trace debugging.

---

## 5. Creational Patterns (GoF)

### Factory Method & Registry Factory
- **When to use**: Decoupling client code from concrete class instantiation.
- **How**: In Python, use a dictionary registry mapping keys to constructor callables: `REGISTRY[name](**kwargs)`.
- **Trade-offs**: Eliminates hardcoded class dependencies; requires maintaining registry mappings.

### Abstract Factory
- **When to use**: Creating families of related, matching products (e.g. GUI theme widgets, database adapter suites).
- **How**: Abstract Factory interface defines creation methods for each family member; concrete factories yield matching objects.
- **Trade-offs**: Enforces visual or functional harmony across families; adding new product types requires updating all factories.\n