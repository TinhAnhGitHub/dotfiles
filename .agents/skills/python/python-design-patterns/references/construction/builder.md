# Builder

## Intent

Accumulate validated configuration and produce a complex object only when construction is complete.

## Use when

Use a Builder when construction has many optional or ordered steps, intermediate validation, or
multiple related output forms. Prefer keyword arguments or a dataclass for simple configuration.

## Why

The builder separates readable configuration from final construction and can prevent partially
initialized objects.

## Example

```python
from dataclasses import dataclass, field

@dataclass
class PipelineBuilder:
    steps: list[str] = field(default_factory=list)

    def add(self, step: str) -> "PipelineBuilder":
        self.steps.append(step)
        return self

    def build(self) -> tuple[str, ...]:
        if not self.steps:
            raise ValueError("a pipeline needs at least one step")
        return tuple(self.steps)
```

This solves fragile constructors with positional optional arguments and late validation.

## When not to use

Do not add a mutable builder for a two-field object. A frozen configuration model is safer when
steps do not need to be accumulated.

## Trade-offs and tests

Builders introduce mutable intermediate state and possible reuse bugs. Test step ordering,
validation, failed builds, and whether `build()` returns an immutable snapshot.

## Framework examples

### TRL — `SFTConfig` and `SFTTrainer` (adapted)

```python
from trl import SFTConfig, SFTTrainer

training_args = SFTConfig(
    output_dir="runs/sft",
    num_train_epochs=2,
    per_device_train_batch_size=4,
)
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_set,
    processing_class=tokenizer,
)
trainer.train()
```

This solves constructing a trainer from many optional, validated training choices before the run
starts. It fits Builder because `SFTConfig` accumulates configuration and `SFTTrainer` is created
only after the complete training object is ready. See the official [TRL SFTTrainer
documentation](https://huggingface.co/docs/trl/sft_trainer).
