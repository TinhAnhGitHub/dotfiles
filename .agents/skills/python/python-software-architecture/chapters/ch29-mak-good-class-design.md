# Chapter 29: Good Class Design to Build the Application Right

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 2: Design the Right Application (Chapter 4)

## Core Idea
Well-designed classes exhibit high cohesion and low coupling, adhering strictly to the Single Responsibility Principle and collaborating through clear, minimal interfaces.

## Frameworks Introduced
- **CRC Cards (Class-Responsibility-Collaborator)**:
  - When to use: Early object-oriented design and architectural brainstorming.
  - How: For each candidate class, write an index card divided into three areas:
    1. **Class Name**: Clear noun reflecting the ubiquitous language.
    2. **Responsibilities**: 2–4 high-level obligations the class fulfills.
    3. **Collaborators**: Other classes it interacts with to fulfill those obligations.
    - *Rule*: If a card runs out of room on responsibilities, the class does too much; split it!
- **The Cohesion-Coupling Matrix**:
  - When to use: Evaluating the modular health of packages and classes.
  - How: Aim for the top-left quadrant: **High Cohesion** (all methods in a class work on the same state toward a unified goal) and **Low Coupling** (the class knows about as few other classes as possible).

## Key Concepts
- **Cohesion**: The measure of how strongly related the responsibilities of a single class or module are.
- **Coupling**: The degree of direct knowledge or reliance one class has on another.
- **Single Responsibility Principle (SRP)**: Every class should have responsibility over a single part of the program's functionality.
- **Law of Demeter (Principle of Least Knowledge)**: A method of an object should only call methods on itself, its arguments, objects it instantiates, or direct component fields (don't talk to strangers).

## Mental Models
- **The Swiss Army Knife vs. Professional Chef's Knife**: A Swiss Army knife does 30 things poorly (low cohesion God class); a chef's knife does slicing with supreme excellence (high cohesion class).
- **Train Wrecks Violate Demeter**: Code like `order.get_customer().get_profile().get_address().get_zip()` is a train wreck that couples the caller to 4 nested internal representations.

## Anti-patterns
- **God Class / Blob**: A massive class with hundreds of lines, dozens of attributes, and myriad unrelated methods.
- **Feature Envy**: A method in Class A that spends more time reading and writing the fields of Class B than its own; move that method into Class B!
- **Data Clumps**: The same 3–4 primitive parameters (e.g. `street`, `city`, `state`, `zip`) passed together across multiple functions; bundle them into an `Address` Value Object.

## Code Examples

```python
# 1. Low Cohesion & High Coupling (Anti-pattern)
class StudentRecordManager:
    def __init__(self, db_conn):
        self.db = db_conn

    def calculate_gpa(self, grades: list[float]) -> float:
        return sum(grades) / len(grades)

    def print_report_card(self, student_id: str) -> None:
        # SQL query, business math, and terminal formatting in one class!
        data = self.db.query(f"SELECT * FROM students WHERE id={student_id}")
        print(f"Student: {data['name']}")

# 2. High Cohesion & Low Coupling (Refactored)
@dataclass(frozen=True)
class Grade:
    course: str
    points: float

class Student:
    """High Cohesion: Focuses exclusively on student domain rules."""
    def __init__(self, student_id: str, name: str):
        self.id = student_id
        self.name = name
        self._grades: list[Grade] = []

    def add_grade(self, grade: Grade) -> None:
        self._grades.append(grade)

    @property
    def gpa(self) -> float:
        if not self._grades:
            return 0.0
        return sum(g.points for g in self._grades) / len(self._grades)

class ReportCardFormatter:
    """High Cohesion: Focuses exclusively on presentation formatting."""
    @staticmethod
    def format_text(student: Student) -> str:
        return f"Student: {student.name} | GPA: {student.gpa:.2f}"
```
- **What it demonstrates**: Splitting a low-cohesion manager class into a cohesive domain entity (`Student`) and a focused presentation formatter (`ReportCardFormatter`).

## Reference Tables

| Metric | Ideal Target | Tell / Smell of Failure |
|---|---|---|
| **Cohesion** | High (focused single purpose) | Methods do not share instance variables |
| **Coupling** | Low (collaborates via abstractions) | Changing one class breaks 5 other files |
| **Size** | Small (< 100–200 lines per class) | Class requires endless scrolling |
| **Knowledge** | Honors Law of Demeter | Long chained method calls (`a.b().c().d()`) |

## Worked Example
Applying CRC cards to design a flight booking system:
- **Card 1: `Flight`**
  - *Responsibilities*: Track available seats, allocate seat, check capacity.
  - *Collaborators*: `Seat`, `Passenger`.
- **Card 2: `Reservation`**
  - *Responsibilities*: Link passenger to flight, calculate ticket price.
  - *Collaborators*: `Flight`, `Passenger`, `PricePolicy`.
- Notice that database persistence and payment processing are NOT on these cards; they belong to collaborator adapters!

## Key Takeaways
1. High cohesion and low coupling are the two guiding stars of modular object-oriented design.
2. Use CRC cards during initial design to keep class responsibilities tightly scoped.
3. Avoid Feature Envy: place methods where the data they operate on lives.
4. Respect the Law of Demeter to avoid fragile chained method calls.

## Connects To
- **Ch 28**: Deriving cohesive classes from requirements.
- **Ch 30**: Hiding class implementations to reduce coupling.
- **Ch 15**: Single Responsibility Principle in Python.
