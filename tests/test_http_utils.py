import pytest

from inland_empire.utils.http_utils import _sleep_seconds, fetch_with_backoff


class _Response:
    def __init__(self, status_code, text="ok", headers=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _FakeSession:
    """Returns queued responses, recording how many calls were made."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def get(self, url, timeout=None):
        self.calls += 1
        result = self._responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Keeps retry tests instant instead of actually backing off."""

    async def _instant(_seconds):
        return None

    monkeypatch.setattr("inland_empire.utils.http_utils.asyncio.sleep", _instant)


@pytest.mark.asyncio
async def test_returns_body_without_retrying():
    session = _FakeSession([_Response(200, "body")])

    assert await fetch_with_backoff(session, "http://x", 30) == "body"
    assert session.calls == 1


@pytest.mark.asyncio
async def test_retries_on_rate_limit_then_succeeds():
    session = _FakeSession([_Response(429), _Response(200, "body")])

    assert await fetch_with_backoff(session, "http://x", 30) == "body"
    assert session.calls == 2


@pytest.mark.asyncio
async def test_retries_on_forbidden():
    """Letterboxd throttles with 403, so it must be retried rather than raised."""
    session = _FakeSession([_Response(403), _Response(200, "body")])

    assert await fetch_with_backoff(session, "http://x", 30) == "body"
    assert session.calls == 2


@pytest.mark.asyncio
async def test_retries_on_server_error():
    session = _FakeSession([_Response(503), _Response(500), _Response(200, "body")])

    assert await fetch_with_backoff(session, "http://x", 30) == "body"
    assert session.calls == 3


@pytest.mark.asyncio
async def test_retries_on_network_error():
    session = _FakeSession([ConnectionError("boom"), _Response(200, "body")])

    assert await fetch_with_backoff(session, "http://x", 30) == "body"
    assert session.calls == 2


@pytest.mark.asyncio
async def test_raises_after_exhausting_retries():
    session = _FakeSession([_Response(429) for _ in range(5)])

    with pytest.raises(RuntimeError):
        await fetch_with_backoff(session, "http://x", 30)
    assert session.calls == 5


def test_backoff_grows_and_respects_retry_after():
    # Compare averages: jitter makes any single pair of draws overlap-prone
    early = sum(_sleep_seconds(0, None) for _ in range(50)) / 50
    later = sum(_sleep_seconds(3, None) for _ in range(50)) / 50
    assert early < later

    # The cap holds even after jitter is applied
    assert all(_sleep_seconds(99, None) <= 60.0 for _ in range(50))

    # An explicit Retry-After header wins over the computed delay
    assert _sleep_seconds(0, "12") == 12.0

    # A malformed header falls back to exponential backoff
    assert _sleep_seconds(0, "soon") > 0
