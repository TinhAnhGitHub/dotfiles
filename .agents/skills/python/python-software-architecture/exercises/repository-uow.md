# Exercise — Repository, Aggregate, and Unit of Work

## Goal

Implement P01–P05 for a small allocation service: domain rules stay pure, the use case depends on ports, and two writes commit atomically.

## Starting point

Create a `Sku`, `Batch`, and `Allocation` model. A batch cannot allocate more units than it owns, and the same order cannot be allocated twice.

## Sequence

1. Implement the invariant in the aggregate; do not put it in the repository.
2. Define `BatchRepository` and `UnitOfWork` with `Protocol`.
3. Build an in-memory fake UoW and a production-shaped adapter.
4. Write an `allocate(order_id, sku)` use case that runs inside `with uow:`.
5. Add a second adapter without changing the use case.

## Tests to require

- invalid quantities fail before persistence;
- a duplicate allocation is idempotent or raises the documented domain error;
- a failed second write triggers rollback;
- the fake and real adapter satisfy the same repository contract;
- the use case imports no ORM or web framework.

## Production comparison

Read the P03/P04 pattern page and compare the repository/UoW sections of the Transformers, vLLM, and HTTPX dossiers once available. Explain why a high-throughput system may batch or bypass a repository for reads.

## Deliverable

A small package with domain, application ports, adapters, and tests, plus a short note identifying the transaction boundary and one case where a direct query would be simpler.

