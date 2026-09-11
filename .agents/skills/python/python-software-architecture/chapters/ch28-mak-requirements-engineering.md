# Chapter 28: Get Requirements to Build the Right Application

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 2: Design the Right Application (Chapter 3)

## Core Idea
Before designing the application right (architecture and classes), software engineers must ensure they are designing the right application by systematically discovering, refining, and translating domain requirements into clear user stories and domain entities.

## Frameworks Introduced
- **The Requirements-to-Model Translation Framework**:
  - When to use: Extracting domain objects and responsibilities from natural language business requirements.
  - How:
    1. **Nouns -> Candidate Classes / Entities**: Identify key nouns in user stories (e.g. `Customer`, `Account`, `Reservation`).
    2. **Verbs -> Methods / Operations**: Identify actions and state changes (e.g. `withdraw`, `transfer`, `cancel`).
    3. **Adjectives / Quantities -> Value Objects / Attributes**: Identify descriptive data (e.g. `balance`, `currency`, `due_date`).
    4. **Constraints -> Invariants**: Identify rules containing "must", "cannot", "at least" (e.g. "balance cannot drop below zero").
- **User Story + Acceptance Criteria (Given-When-Then)**:
  - When to use: Defining unambiguous feature specifications that map directly to automated tests.
  - How: Structure as: `As a <role>, I want <feature>, so that <business benefit>`. Attach scenarios in Gherkin syntax (`Given... When... Then...`).

## Key Concepts
- **Functional Requirements**: What the software must do (e.g. calculate interest, generate invoices).
- **Non-Functional Requirements (Quality Attributes)**: How the software must perform (latency, security, scalability, maintainability).
- **Domain Modeling**: Abstracting real-world entities and workflows into software classes that mirror the problem domain.
- **Ubiquitous Language**: An unambiguous vocabulary shared between domain experts and software engineers.

## Mental Models
- **Requirements as the Blueprint, Architecture as the Foundation**: Laying bricks before confirming the room layout results in demolishing walls. Requirements define what needs support.
- **The Noun-Verb Filter**: Highlight user stories with highlighters: yellow for nouns (classes), blue for verbs (methods), green for rules (invariants).

## Anti-patterns
- **Assuming Requirements**: Guessing what stakeholders need without interviewing them or validating edge cases.
- **Conflating Requirements with Implementation**: Writing requirements like "Store customer records in PostgreSQL table with UUID primary key"; that is an implementation detail, not a requirement.
- **Scope Creep Without Prioritization**: Adding unrequested features ("gold-plating") instead of satisfying validated user needs.

## Code Examples

```python
# User Story:
# As a library member, I want to borrow a book, so that I can read it at home.
# Acceptance Criteria:
# - Given an available book and a member with fewer than 5 active loans
# - When the member borrows the book
# - Then the book becomes borrowed, and a loan record is created with a 14-day due date.

from datetime import date, timedelta
from dataclasses import dataclass

class LoanLimitExceeded(Exception): ...
class BookNotAvailable(Exception): ...

@dataclass(frozen=True)
class BookId:
    isbn: str

class Book:
    def __init__(self, book_id: BookId, title: str):
        self.id = book_id
        self.title = title
        self.is_borrowed = False

    def mark_borrowed(self) -> None:
        if self.is_borrowed:
            raise BookNotAvailable(f"Book {self.title} is already on loan")
        self.is_borrowed = True

class Member:
    MAX_LOANS = 5

    def __init__(self, member_id: str, name: str):
        self.id = member_id
        self.name = name
        self._loans: list[Book] = []

    def borrow_book(self, book: Book, loan_date: date) -> tuple[Book, date]:
        if len(self._loans) >= self.MAX_LOANS:
            raise LoanLimitExceeded("Member has reached maximum active loans")
        book.mark_borrowed()
        self._loans.append(book)
        due_date = loan_date + timedelta(days=14)
        return book, due_date
```
- **What it demonstrates**: Direct, 1-to-1 translation from user story acceptance criteria to pure Python domain entities, methods, and exceptions.

## Reference Tables

| Grammatical Element | Software Design Artifact | Example from Domain |
|---|---|---|
| **Noun (Common)** | Class / Entity | `Book`, `Member`, `Loan` |
| **Noun (Descriptor)**| Attribute / Value Object | `isbn`, `due_date`, `title` |
| **Verb (Active)** | Method on Class | `borrow_book()`, `mark_borrowed()` |
| **Modal Rule (Must/Cannot)** | Invariant Validation / Exception | `if len(loans) >= 5: raise ...` |

## Worked Example
Translating requirements for an ATM withdrawal:
- *Requirement*: "A customer cannot withdraw more cash than their daily withdrawal limit of $500, nor more than their available balance."
- *Domain Entities*: `Customer`, `Account`, `DailyLimitTracker`
- *Invariants*:
  1. `amount <= account.balance` -> raises `InsufficientFunds`
  2. `daily_total + amount <= 500` -> raises `DailyLimitExceeded`
- *Implementation*: Enforce both constraints inside `Account.withdraw(amount)` before altering state.

## Key Takeaways
1. Building the right application takes precedence over technical architectural perfection.
2. Translate nouns into candidate classes and verbs into class operations.
3. Express business constraints as explicit domain invariants and custom exceptions.
4. Keep technical database and framework terms out of core domain requirements.

## Connects To
- **Ch 1**: Domain modeling in Percival's architecture.
- **Ch 29**: Designing cohesive classes from requirements.
- **Ch 17**: Clean Architecture Domain-Driven Design core.
