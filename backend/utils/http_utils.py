import asyncio
import random

# Letterboxd throttles bursts; back off instead of hammering it.
MAX_RETRIES = 5
INITIAL_BACKOFF = 0.5
BACKOFF_FACTOR = 1.0
MAX_BACKOFF = 60.0
JITTER = 0.3
# Letterboxd returns 403 (not 429) when it throttles a burst of requests,
# and it clears on its own, so treat it as retryable.
RETRY_STATUSES = {403, 429, 500, 502, 503, 504}


class RateLimitError(RuntimeError):
    """Raised when a URL keeps failing after exhausting all retries."""


def _sleep_seconds(attempt: int, retry_after: str | None) -> float:
    """Exponential backoff with jitter, respecting Retry-After when present."""
    if retry_after:
        try:
            return min(float(retry_after), MAX_BACKOFF)
        except ValueError:
            pass

    delay = min(INITIAL_BACKOFF * (BACKOFF_FACTOR**attempt), MAX_BACKOFF)
    # Jitter avoids a thundering herd when many requests retry together.
    # Clamp afterwards so jitter can't push the delay past the cap.
    return min(delay * (1 + random.uniform(-JITTER, JITTER)), MAX_BACKOFF)


async def fetch_with_backoff(session, url: str, timeout: int) -> str:
    """Fetches a URL, retrying on rate limits and transient server errors."""
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = await asyncio.to_thread(session.get, url, timeout=timeout)
        except Exception as e:  # network/timeout errors are worth retrying too
            last_error = e
        else:
            if response.status_code not in RETRY_STATUSES:
                response.raise_for_status()
                return response.text

            last_error = RateLimitError(f"HTTP {response.status_code} for {url}")
            if attempt < MAX_RETRIES - 1:
                retry_after = response.headers.get("Retry-After")
                await asyncio.sleep(_sleep_seconds(attempt, retry_after))
                continue

        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(_sleep_seconds(attempt, None))

    raise RateLimitError(
        f"Failed to fetch {url} after {MAX_RETRIES} attempts: {last_error}"
    )
