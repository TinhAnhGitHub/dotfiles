# Chapter 36: The Iterator and Visitor Design Patterns

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 4: Design Patterns (Chapter 11)

## Core Idea
Iterator provides a way to access the elements of an aggregate object sequentially without exposing its underlying representation; Visitor separates algorithms and operations from the complex object structures on which they operate.

## Frameworks Introduced
- **The Iterator Pattern (Behavioral)**:
  - When to use: Traversing custom data structures (trees, graphs, composite collections) without leaking internal storage nodes.
  - How: In Python, implement the iterator protocol: `__iter__()` returning the iterator object, and `__next__()` returning elements and raising `StopIteration` at the end. Use generator functions (`yield`) for concise implementations.
- **The Visitor Pattern (Behavioral)**:
  - When to use: When you need to perform operations across a heterogeneous composite hierarchy (e.g. an Abstract Syntax Tree) without polluting node classes with operation methods.
  - How: Define a Visitor interface with `visit_<element>()` methods. Element classes accept a visitor (`element.accept(visitor)`), which dispatches back to `visitor.visit_<element>(self)`.

## Key Concepts
- **Python Iterator Protocol**: The `__iter__()` and `__next__()` methods enabling the standard `for item in collection:` loop.
- **Generator Function**: A function containing `yield` statements that automatically creates an iterator.
- **Double Dispatch**: The mechanism in the Visitor pattern where execution depends on both the runtime type of the Visitor and the runtime type of the Element.
- **AST (Abstract Syntax Tree)**: A hierarchical tree representing source code or domain expressions, the premier use case for the Visitor pattern.

## Mental Models
- **Iterator as a Guided Museum Tour**: You don't need to know the floor plan or access the back storage rooms; the tour guide steps you room-by-room through the exhibits.
- **Visitor as a City Inspector**: The buildings in a city (AST nodes: Residential, Commercial, Industrial) don't know how to assess taxes or inspect fire hazards. The `TaxVisitor` visits each building, reads its properties, and computes taxes.

## Anti-patterns
- **Exposing Internal Pointer Nodes**: Returning raw linked-list nodes or tree pointer references to client callers.
- **Modifying AST Classes for Every New Operation**: Adding `eval()`, `pretty_print()`, `type_check()`, and `compile()` methods to every AST node class, bloating them with unrelated code.
- **Ignoring Python Generators**: Writing 40 lines of boilerplate state machine classes when a 4-line generator with `yield` satisfies the iterator protocol.

## Code Examples

```python
# 1. ITERATOR PATTERN via Python Generator
class BinaryTree:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def __iter__(self):
        # In-order traversal using Python generator
        if self.left:
            yield from self.left
        yield self.value
        if self.right:
            yield from self.right

# 2. VISITOR PATTERN on Expression AST
class ASTNode(ABC):
    @abstractmethod
    def accept(self, visitor: "ASTVisitor"): ...

class NumberNode(ASTNode):
    def __init__(self, value: int):
        self.value = value
    def accept(self, visitor): visitor.visit_number(self)

class AddNode(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right
    def accept(self, visitor): visitor.visit_add(self)

class ASTVisitor(ABC):
    @abstractmethod
    def visit_number(self, node: NumberNode): ...
    @abstractmethod
    def visit_add(self, node: AddNode): ...

class EvaluatorVisitor(ASTVisitor):
    def __init__(self):
        self.result = 0

    def visit_number(self, node: NumberNode):
        self.result = node.value

    def visit_add(self, node: AddNode):
        node.left.accept(self)
        left_val = self.result
        node.right.accept(self)
        right_val = self.result
        self.result = left_val + right_val
```
- **What it demonstrates**: Pythonic generator-based in-order traversal (Iterator) and double-dispatch AST evaluation (Visitor) without polluting tree nodes.

## Reference Tables

| Feature | Iterator Pattern | Visitor Pattern |
|---|---|---|
| **Primary Intent** | Sequential traversal of elements | Executing operations on element structures |
| **Object Structure** | Homogeneous or linear collections | Heterogeneous tree / composite structures |
| **Python Tooling** | `__iter__`, `__next__`, `yield` | Double dispatch (`accept(visitor)`) |
| **Modification Openness**| Open for new data structures | Open for new operations on fixed structures |

## Worked Example
Adding a Pretty-Printer visitor to the AST without modifying `NumberNode` or `AddNode`:

```python
class PrettyPrinterVisitor(ASTVisitor):
    def __init__(self):
        self.output = ""

    def visit_number(self, node: NumberNode):
        self.output = str(node.value)

    def visit_add(self, node: AddNode):
        node.left.accept(self)
        left_str = self.output
        node.right.accept(self)
        right_str = self.output
        self.output = f"({left_str} + {right_str})"
```
Tree nodes remain unchanged; a completely new capability was added cleanly.

## Key Takeaways
1. Implement the Python iterator protocol using generator functions (`yield`) for clean traversals.
2. Visitor enables adding operations to complex object structures without modifying their classes.
3. Visitor is ideal for Abstract Syntax Trees, compilers, and document structures.
4. Keep traversal logic separate from computational operations.

## Connects To
- **Ch 39**: Composite pattern hierarchies visited by Visitors.
- **Ch 15**: Open/Closed Principle via Visitor extensions.
- **Ch 40**: Recursive traversal techniques.
