# Specification

## Intent

Represent a business or filtering rule as a composable predicate.

## Use when

Use Specification when rules must be combined with `and`, `or`, or `not`, reused across queries,
or tested independently from the operation that consumes them.

## Why

The rule becomes data with a small contract, making combinations visible and reducing scattered
conditionals.

## Example

```python
from collections.abc import Callable
from functools import reduce
from operator import and_

Spec = Callable[[dict[str, object]], bool]

def all_of(*rules: Spec) -> Spec:
    return lambda item: reduce(and_, (rule(item) for rule in rules), True)
```

This solves repeated, independently testable eligibility or filtering rules.

## When not to use

Keep one local conditional when composition is not needed. Avoid opaque predicate objects whose
diagnostics cannot explain which rule rejected an item.

## Trade-offs and tests

Short-circuiting and error semantics matter. Test empty composition, nested combinations, and
diagnostic output if rules are user-visible.

## Framework evidence

Qdrant payload filters provide a strong composable-filter analogue; retrieval and reward systems
can use the same shape. Treat the framework mapping as conceptual unless source evidence is linked.

## Framework examples

### DSPy — `Signature` as an explicit contract

DSPy solves the problem of scattering input/output requirements through prompt strings and
callers. A `Signature` fits the Specification idea because the contract is named, reusable, and
independently testable; application predicates can still compose around it when boolean filtering
is required.

```python
import dspy

class Answer(dspy.Signature):
    question = dspy.InputField()
    answer = dspy.OutputField(desc="supported, concise answer")

answerer = dspy.Predict(Answer)
```

Adapted from the [DSPy signatures API](https://dspy.ai/api/signatures/)
(3.x, fetched 2026-08-30; adapted analogue).
