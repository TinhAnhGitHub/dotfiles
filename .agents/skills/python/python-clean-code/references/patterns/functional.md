# Functional boundaries

## Use when

Use first-class functions when behavior varies independently from data: sorting, filtering,
callbacks, hooks, strategies, deferred calls, or runtime dispatch.

## Why

Functions make behavior replaceable and testable without multiplying subclasses. They also make
configuration explicit when passed into a constructor or factory.

## Core patterns

- Use `itemgetter`, `attrgetter`, and `methodcaller` for named, reusable extraction.
- Use `operator.add` and related functions when an operator must be passed as data.
- Use `functools.partial` for transparent argument binding; wrap it when metadata is required.
- Use a callable object when behavior has durable state or a public lifecycle.
- Use a dispatch table when branches select a complete operation by key.
- Use a registry when third parties or separate modules must add implementations.

## When not to use

Keep a local lambda or `if` statement when the behavior is one-use, obvious, and unlikely to grow.
Do not create a registry merely to hide a small fixed set of branches.

## Example

```python
from collections.abc import Callable

Formatter = Callable[[str], str]

def render(value: str, formatter: Formatter) -> str:
    return formatter(value)

formats: dict[str, Formatter] = {
    "plain": str,
    "upper": str.upper,
}
```

This solves a growing formatter `if`/`elif` chain while keeping the contract easy to test.

## Tests and pitfalls

Test unknown keys, registration order if meaningful, callable metadata, and exceptions. Do not
forget that `itemgetter(a, b)` returns a tuple and that `partial` does not provide `__name__`.

## Framework examples

These are short, adapted shapes; the framework owns the surrounding lifecycle.

### verl — role-to-worker dispatch

```python
workers = {"actor": ActorWorker, "critic": CriticWorker}
worker = workers[role](config)
```

`role_worker_mapping` keeps PPO orchestration independent of the selected worker implementation
and makes backend selection testable as data. See the [verl PPO architecture](https://verl.readthedocs.io/en/latest/examples/ppo_code_architecture.html).

### Agno — registered tools

```python
toolkit = Toolkit(name="search")
toolkit.register(search_documents)
```

`Toolkit.register` solves the need to add tools without editing the caller; a registry fits because
each tool is a named callable with the same execution boundary. See the [Agno SDK](https://docs.agno.com/sdk/introduction).

### TRL — injectable reward functions

```python
def correctness(completions: list[str], **_) -> list[float]:
    return [float(answer_is_valid(text)) for text in completions]

trainer = GRPOTrainer(
    model=model, args=training_args, reward_funcs=correctness, train_dataset=dataset
)
```

`reward_funcs` replaces a growing conditional reward policy with independently testable functions.
See the [TRL GRPOTrainer documentation](https://huggingface.co/docs/trl/grpo_trainer).

### slime — rollout hook injection

```python
def custom_generate(requests, model):
    return model.generate(requests)

config.custom_generate_function_path = "my_project.rollouts:custom_generate"
```

The configured function changes rollout behavior while the training loop remains reusable, which is
the registry/injection form of a functional boundary. See [slime customization](https://thudm.github.io/slime/get_started/customization.html).

## Trade-offs

First-class callables keep behavior replaceable and easy to test, but indirection can make control
flow harder to trace. Keep dispatch tables and registries small, named, and explicit about unknown keys.

## ArjanCodes 2026 examples (adapted)

The 2026 examples distinguish duplicated knowledge from duplicated structure, flatten nested
control flow, keep natural patterns functional, and make policy selection explicit.

### DRY the rule, not every line

If username and email normalization share a rule, extract that rule. Do not force both workflows
through a flag-heavy generic function merely because their loops look similar.

```python
def normalize_username(value: str) -> str:
    return value.strip().lower()


def normalize_email(value: str) -> str:
    return value.strip().lower()


def valid_email(value: str) -> bool:
    return "@" in value
```

The small structural repetition keeps the two change axes visible. Adapted from the [2026 `dry`
examples](https://github.com/ArjanCodes/examples/tree/main/2026/dry).

### Flatten nested control flow at the boundary

Give a nested loop or condition a named operation when it has business meaning.

```python
def active_names(groups: list[list[dict[str, str]]]) -> list[str]:
    return [
        person["name"]
        for group in groups
        for person in group
        if person.get("active") == "yes"
    ]
```

Use this only when the extracted operation has a stable meaning; a one-line nested comprehension
may be clearer inline. Adapted from the [2026 `nested` examples](https://github.com/ArjanCodes/examples/tree/main/2026/nested).

### Let the natural pattern stay functional

Do not introduce a Pattern class just to wrap a list of functions when the steps have no identity or
lifecycle.

```python
from collections.abc import Callable

Stage = Callable[[str], str]


def apply_stages(value: str, stages: list[Stage]) -> str:
    for stage in stages:
        value = stage(value)
    return value
```

The collection of stages is the composition point, and each stage is independently testable. See
the [2026 `pattern` examples](https://github.com/ArjanCodes/examples/tree/main/2026/pattern).

### Policy and registry as explicit data

When rules are independently enabled, a policy registry avoids a growing boolean-flag branch while
keeping unknown names fail-fast.

```python
from collections.abc import Callable
from dataclasses import replace
from functools import reduce

Policy = Callable[[User, Request], Request]


def grant_access(user: User, request: Request) -> Request:
    return replace(request, access_granted=True)


POLICY_REGISTRY: dict[str, Policy] = {"grant_access": grant_access}


def apply_policies(user: User, request: Request, names: list[str]) -> Request:
    try:
        policies = [POLICY_REGISTRY[name] for name in names]
    except KeyError as error:
        raise ValueError(f"unknown policy: {error.args[0]}") from error
    return reduce(lambda current, policy: policy(user, current), policies, request)
```

The registry fits because policies share one callable contract and are selected by configuration.
See the [2026 `policy` examples](https://github.com/ArjanCodes/examples/tree/main/2026/policy) and
the [policy video](https://www.youtube.com/watch?v=wYeDGkdMi3g).

## zedr clean-code-python diagnostics (adapted)

The [zedr clean-code-python table of contents](https://github.com/zedr/clean-code-python#table-of-contents)
adds practical diagnostics to these callable boundaries: use searchable names, keep one level of
abstraction, avoid boolean flags, centralize side effects, and apply DRY to duplicated knowledge.

```python
def create_file(name: str) -> None:
    Path(name).touch()


def create_temp_file(name: str) -> None:
    (Path(gettempdir()) / name).touch()
```

Two named operations are clearer than `create_file(name, temp=True)`: the flag was evidence that
the function had two responsibilities. Keep the filesystem effect at these explicit boundaries and
make the transformation helpers pure where possible.
