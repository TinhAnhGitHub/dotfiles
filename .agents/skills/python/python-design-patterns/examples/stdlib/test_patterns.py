from __future__ import annotations

import unittest

from patterns import (
    ALLOWED,
    AppSettings,
    BackgroundPreloader,
    CommandRegistry,
    DomainError,
    EventBus,
    InMemoryInventoryAdapter,
    InvalidQuantity,
    InventoryPort,
    lazy_stream,
    OrderHistory,
    OrderPlaced,
    OrderQueue,
    OrderReader,
    OrderRequest,
    OrderWriter,
    OutOfStock,
    Status,
    SyncOptions,
    SyncSummary,
    TokenBucketRateLimiter,
    TTLCache,
    WorkflowState,
    apply_strategy,
    compose_logger,
    counted,
    load_settings,
    nonempty,
    place_order,
    registry,
    sync_records,
    UnknownSku,
)


class PatternTests(unittest.TestCase):
    def test_composition_combines_filter_and_output(self) -> None:
        output: list[str] = []
        log = compose_logger(output.append, lambda message: "keep" in message)

        log("drop")
        log("keep")

        self.assertEqual(output, ["keep"])

    def test_registry_rejects_duplicate_names(self) -> None:
        factories: dict[str, object] = {}
        register = registry(factories, "memory")
        register(lambda: "one")

        with self.assertRaisesRegex(ValueError, "duplicate"):
            register(lambda: "two")

    def test_command_registry_dispatch_and_duplicate(self) -> None:
        reg = CommandRegistry()

        @reg.register("text", "count")
        def count_words(text: str) -> int:
            return len(text.split())

        self.assertEqual(reg.dispatch("text", "count", "hello world foo"), 3)

        with self.assertRaisesRegex(ValueError, "duplicate command registration: text:count"):
            @reg.register("text", "count")
            def duplicate_count(text: str) -> int:
                return len(text)

    def test_command_registry_missing_key_and_defensive_copy(self) -> None:
        reg = CommandRegistry()

        @reg.register("text", "shout")
        def shout(text: str) -> str:
            return f"{text.upper()}!"

        with self.assertRaisesRegex(KeyError, "unknown command: text:unknown"):
            reg.dispatch("text", "unknown", "test")

        commands = reg.get_commands()
        commands[("text", "fake")] = lambda: "fake"
        self.assertNotIn(("text", "fake"), reg.get_commands())

    def test_strategy_is_replaceable(self) -> None:
        self.assertEqual(apply_strategy("hello", str.upper), "HELLO")
        self.assertEqual(apply_strategy("hello", lambda value: value[::-1]), "olleh")

    def test_decorator_preserves_metadata(self) -> None:
        @counted
        def add(left: int, right: int) -> int:
            return left + right

        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add.__name__, "add")
        self.assertEqual(add.__annotations__["return"], "int")

    def test_state_machine_rejects_invalid_transition(self) -> None:
        state = WorkflowState()
        self.assertIn(Status.RUNNING, ALLOWED[state.status])
        with self.assertRaisesRegex(ValueError, "invalid transition"):
            state.transition(Status.DONE)

    def test_event_bus_notifies_listeners(self) -> None:
        events: list[str] = []
        bus = EventBus()
        bus.subscribe(events.append)
        bus.publish("started")
        self.assertEqual(events, ["started"])

    def test_lazy_filter(self) -> None:
        self.assertEqual(list(nonempty(["", " a ", "  "])), [" a "])

    def test_substitutability_and_interface_segregation(self) -> None:
        history = OrderHistory(["ORD-1", "ORD-2"])
        # History satisfies Reader, but not Writer (LSP preserved, no pretender write method)
        self.assertTrue(isinstance(history, OrderReader))
        self.assertFalse(isinstance(history, OrderWriter))
        self.assertEqual(history.get_orders(), ["ORD-1", "ORD-2"])

        # Mutating copy doesn't mutate history
        orders = history.get_orders()
        orders.append("ORD-3")
        self.assertEqual(history.get_orders(), ["ORD-1", "ORD-2"])

        # Queue satisfies both Reader and Writer
        queue = OrderQueue()
        self.assertTrue(isinstance(queue, OrderReader))
        self.assertTrue(isinstance(queue, OrderWriter))
        queue.enqueue("ORD-NEW")
        self.assertEqual(queue.get_orders(), ["ORD-NEW"])

    def test_sync_records_options_composition(self) -> None:
        class FakeSink:
            def __init__(self, fail_count: int = 0) -> None:
                self.failures_remaining = fail_count
                self.saved: list[str] = []

            def save_records(self, records: list[str]) -> None:
                if self.failures_remaining > 0:
                    self.failures_remaining -= 1
                    raise ConnectionError("network blip")
                self.saved = records.copy()

        # 1. Validation flag caught invalid record
        sink = FakeSink()
        with self.assertRaisesRegex(ValueError, "records cannot be blank"):
            sync_records(sink, ["valid", "   "], SyncOptions(validate=True))

        # 2. Blank record allowed when validation disabled
        res1 = sync_records(sink, ["valid", "   "], SyncOptions(validate=False))
        self.assertEqual(res1, SyncSummary(synced_count=2, attempts=1))

        # 3. Retry options succeed on attempt 2
        failing_sink = FakeSink(fail_count=1)
        res2 = sync_records(failing_sink, ["item1"], SyncOptions(max_attempts=3))
        self.assertEqual(res2, SyncSummary(synced_count=1, attempts=2))
        self.assertEqual(failing_sink.saved, ["item1"])

        # 4. Failures exceeding max_attempts raise error
        exhausted_sink = FakeSink(fail_count=5)
        with self.assertRaises(ConnectionError):
            sync_records(exhausted_sink, ["item1"], SyncOptions(max_attempts=2))

    def test_token_bucket_rate_limiter(self) -> None:
        current_time = 1000.0

        def fake_clock() -> float:
            return current_time

        limiter = TokenBucketRateLimiter(rate=2.0, capacity=3.0, clock=fake_clock)

        # Initial capacity allows 3 immediate requests
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        # 4th request exhausted tokens
        self.assertFalse(limiter.allow_request())

        # Advance 1 second -> replenishes 2 tokens
        current_time += 1.0
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

        # Invalid configuration raises ValueError
        with self.assertRaises(ValueError):
            TokenBucketRateLimiter(rate=0, capacity=5)

    def test_12_factor_settings_loader(self) -> None:
        # Default environment fallback
        defaults = load_settings({})
        self.assertEqual(defaults.api_url, "http://localhost:8000")
        self.assertEqual(defaults.database_url, "sqlite:///./app.db")
        self.assertEqual(defaults.log_level, "INFO")
        self.assertEqual(defaults.rate_limit_per_minute, 60)

        # Custom environment mapping overrides defaults
        custom_env = {
            "API_URL": "https://api.example.com",
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/proddb",
            "LOG_LEVEL": "WARNING",
            "RATE_LIMIT_PER_MINUTE": "120",
        }
        custom = load_settings(custom_env)
        self.assertEqual(custom.api_url, "https://api.example.com")
        self.assertEqual(custom.database_url, "postgresql://user:pass@localhost:5432/proddb")
        self.assertEqual(custom.log_level, "WARNING")
        self.assertEqual(custom.rate_limit_per_minute, 120)

    def test_ports_and_adapters_successful_order(self) -> None:
        adapter = InMemoryInventoryAdapter({"SKU-1": 10, "SKU-2": 5})
        self.assertTrue(isinstance(adapter, InventoryPort))

        req = OrderRequest(sku="SKU-1", quantity=4)
        result = place_order(req, adapter)

        self.assertEqual(result, OrderPlaced(sku="SKU-1", quantity_reserved=4))
        self.assertEqual(adapter.get_stock("SKU-1"), 6)
        self.assertEqual(adapter.get_stock("SKU-2"), 5)

    def test_ports_and_adapters_invalid_quantity(self) -> None:
        adapter = InMemoryInventoryAdapter({"SKU-1": 10})

        with self.assertRaisesRegex(InvalidQuantity, "Quantity must be positive"):
            place_order(OrderRequest(sku="SKU-1", quantity=0), adapter)

        with self.assertRaisesRegex(InvalidQuantity, "Quantity must be positive"):
            place_order(OrderRequest(sku="SKU-1", quantity=-3), adapter)

        self.assertEqual(adapter.get_stock("SKU-1"), 10)

    def test_ports_and_adapters_unknown_sku(self) -> None:
        adapter = InMemoryInventoryAdapter({"SKU-1": 10})

        with self.assertRaisesRegex(UnknownSku, "Unknown SKU: SKU-MISSING"):
            place_order(OrderRequest(sku="SKU-MISSING", quantity=2), adapter)

    def test_ports_and_adapters_out_of_stock(self) -> None:
        adapter = InMemoryInventoryAdapter({"SKU-1": 3})

        with self.assertRaisesRegex(OutOfStock, "Insufficient stock for SKU-1"):
            place_order(OrderRequest(sku="SKU-1", quantity=5), adapter)

        # Inventory unmodified on failure
        self.assertEqual(adapter.get_stock("SKU-1"), 3)

    def test_ttl_cache_hits_and_expiration(self) -> None:
        clock_time = 100.0
        calls = 0

        @TTLCache(seconds=5.0, clock=lambda: clock_time)
        def get_rate(currency: str) -> str:
            nonlocal calls
            calls += 1
            return f"{currency}-{calls}"

        # 1. First invocation computes
        self.assertEqual(get_rate("EUR"), "EUR-1")
        self.assertEqual(calls, 1)

        # 2. Invocation within TTL returns cached value
        clock_time += 4.0  # elapsed 4.0 < 5.0
        self.assertEqual(get_rate("EUR"), "EUR-1")
        self.assertEqual(calls, 1)

        # 3. Invocation after TTL expired recomputes
        clock_time += 2.0  # elapsed 6.0 >= 5.0
        self.assertEqual(get_rate("EUR"), "EUR-2")
        self.assertEqual(calls, 2)

    def test_ttl_cache_argument_isolation(self) -> None:
        calls = 0

        @TTLCache(seconds=10.0)
        def multiply(x: int, y: int = 1) -> int:
            nonlocal calls
            calls += 1
            return x * y

        self.assertEqual(multiply(2, y=3), 6)
        self.assertEqual(multiply(2, y=3), 6)
        self.assertEqual(calls, 1)

        # Distinct argument creates separate cache entry
        self.assertEqual(multiply(2, y=4), 8)
        self.assertEqual(calls, 2)

    def test_lazy_stream_early_exit_and_bounded_work(self) -> None:
        evaluated: list[int] = []

        def source() -> Iterator[int]:
            for i in range(100):
                evaluated.append(i)
                yield i

        stream = lazy_stream(source(), limit=3)
        result = list(stream)

        self.assertEqual(result, [0, 1, 2])
        # Producer stopped early upon reaching limit
        self.assertEqual(evaluated, [0, 1, 2])

    def test_background_preloader_warms_cache(self) -> None:
        def compute_sum() -> int:
            return sum(range(100))

        preloader = BackgroundPreloader(compute_sum)
        result = preloader.get(timeout=2.0)
        self.assertEqual(result, sum(range(100)))


if __name__ == "__main__":
    unittest.main()


