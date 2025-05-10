from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar, cast

from fastapi import FastAPI
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator, metrics

P = ParamSpec("P")
T = TypeVar("T")

# Métricas para generate_ai_support_response
AI_RESPONSE_TIME = Histogram(
    "ai_support_response_time_seconds",
    "Time spent generating AI support response",
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float("inf")),
)

AI_RESPONSE_TOTAL = Counter(
    "ai_support_responses_total",
    "Total number of AI support responses generated",
    ["status"],  # success, error
)

AI_EMBEDDING_TIME = Histogram(
    "ai_embedding_generation_time_seconds",
    "Time spent generating embeddings",
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, float("inf")),
)

AI_DOCUMENT_SEARCH_TIME = Histogram(
    "ai_document_search_time_seconds",
    "Time spent searching for similar documents",
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, float("inf")),
)


def track_embedding_time(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """Decorator to track embedding generation time.

    Args:
        func: Async function to track

    Returns:
        Wrapped function that tracks embedding generation time
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with AI_EMBEDDING_TIME.time():
            return await func(*args, **kwargs)

    return cast(Callable[P, Awaitable[T]], wrapper)


def track_document_search_time(
    func: Callable[P, Awaitable[T]],
) -> Callable[P, Awaitable[T]]:
    """Decorator to track document search time.

    Args:
        func: Async function to track

    Returns:
        Wrapped function that tracks document search time
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with AI_DOCUMENT_SEARCH_TIME.time():
            return await func(*args, **kwargs)

    return cast(Callable[P, Awaitable[T]], wrapper)


def track_response_time(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """Decorator to track total response time and success/error counts.

    Args:
        func: Async function to track

    Returns:
        Wrapped function that tracks response time and counts
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with AI_RESPONSE_TIME.time():
            try:
                result = await func(*args, **kwargs)
                AI_RESPONSE_TOTAL.labels(status="success").inc()
                return result
            except Exception:
                AI_RESPONSE_TOTAL.labels(status="error").inc()
                raise

    return cast(Callable[P, Awaitable[T]], wrapper)


def setup_prometheus_metrics(app: FastAPI) -> None:
    """Configure Prometheus metrics for the application.

    Args:
        app: FastAPI application instance
    """
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="fastapi_inprogress",
        inprogress_labels=True,
    )

    # Add default metrics
    instrumentator.add(metrics.default())

    # Add custom metrics
    instrumentator.add(
        metrics.latency(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )
    instrumentator.add(
        metrics.requests(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )

    # Instrument the app
    instrumentator.instrument(app).expose(app)
