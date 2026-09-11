"""External API and Mock lead enrichment service."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EnrichmentResult:
    """Result returned by lead enrichment providers."""

    status: str  # "enriched", "disabled", "failed"
    score: Optional[float] = None
    segment: Optional[str] = None
    error: Optional[str] = None


class BaseEnrichmentProvider:
    """Interface for enrichment providers."""

    def enrich(self, lead_data: dict[str, Any]) -> EnrichmentResult:
        raise NotImplementedError


class OffEnrichmentProvider(BaseEnrichmentProvider):
    """Provider when enrichment is disabled."""

    def enrich(self, lead_data: dict[str, Any]) -> EnrichmentResult:
        logger.debug("Enrichment is disabled (mode=off)")
        return EnrichmentResult(status="disabled", score=None, segment=None)


class MockEnrichmentProvider(BaseEnrichmentProvider):
    """Deterministic mock provider simulating an external scoring engine."""

    def enrich(self, lead_data: dict[str, Any]) -> EnrichmentResult:
        score = 40.0

        # Deterministic scoring based on provided fields
        if lead_data.get("company"):
            score += 25.0
        if lead_data.get("source") in ("website", "shopify", "sales"):
            score += 20.0
        if lead_data.get("notes"):
            score += 10.0
        if lead_data.get("external_id"):
            score += 5.0

        score = min(score, 100.0)

        if score >= 75.0:
            segment = "high"
        elif score >= 50.0:
            segment = "medium"
        else:
            segment = "low"

        logger.info("Mock enrichment generated: score=%.1f, segment=%s", score, segment)
        return EnrichmentResult(status="enriched", score=score, segment=segment)


class HttpEnrichmentProvider(BaseEnrichmentProvider):
    """HTTP client calling external enrichment endpoints with retries and backoff."""

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        transport: Optional[httpx.BaseTransport] = None,
        backoff_delays: Optional[list[float]] = None,
    ):
        self.api_url = api_url or settings.ENRICHMENT_API_URL
        self.api_key = api_key if api_key is not None else settings.ENRICHMENT_API_KEY
        self.timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else settings.ENRICHMENT_TIMEOUT_SECONDS
        )
        self.transport = transport
        self.backoff_delays = backoff_delays or [0.25, 0.5, 1.0]

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def enrich(self, lead_data: dict[str, Any]) -> EnrichmentResult:
        if not self.api_url:
            logger.warning("HTTP enrichment requested but ENRICHMENT_API_URL is not configured")
            return EnrichmentResult(status="failed", error="ENRICHMENT_API_URL is empty")

        headers = self._build_headers()
        max_attempts = len(self.backoff_delays)  # 3 attempts

        last_error_msg = ""

        with httpx.Client(transport=self.transport, timeout=self.timeout_seconds) as client:
            for attempt in range(max_attempts):
                try:
                    logger.debug(
                        "Sending enrichment request to %s (attempt %d/%d)",
                        self.api_url,
                        attempt + 1,
                        max_attempts,
                    )
                    response = client.post(self.api_url, json=lead_data, headers=headers)

                    # Do NOT retry client errors (4xx) except 429 Too Many Requests
                    if 400 <= response.status_code < 500 and response.status_code != 429:
                        last_error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                        logger.warning(
                            "Permanent client error from enrichment API (HTTP %d). Not retrying.",
                            response.status_code,
                        )
                        return EnrichmentResult(status="failed", error=last_error_msg)

                    # Retry on 429 or server errors (5xx)
                    if response.status_code >= 500 or response.status_code == 429:
                        last_error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                        logger.warning(
                            "Transient HTTP %d received from enrichment API (attempt %d/%d).",
                            response.status_code,
                            attempt + 1,
                            max_attempts,
                        )
                        if attempt < max_attempts - 1:
                            time.sleep(self.backoff_delays[attempt])
                            continue
                        return EnrichmentResult(status="failed", error=last_error_msg)

                    response.raise_for_status()
                    data = response.json()

                    score_val = data.get("score")
                    score = float(score_val) if score_val is not None else 50.0
                    segment = str(data.get("segment", "medium")).lower()

                    logger.info("HTTP enrichment success: score=%.1f, segment=%s", score, segment)
                    return EnrichmentResult(status="enriched", score=score, segment=segment)

                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    last_error_msg = f"{type(exc).__name__}: {str(exc)}"
                    logger.warning(
                        "Enrichment connection issue on attempt %d/%d: %s",
                        attempt + 1,
                        max_attempts,
                        last_error_msg,
                    )
                    if attempt < max_attempts - 1:
                        time.sleep(self.backoff_delays[attempt])
                        continue
                except Exception as exc:
                    last_error_msg = f"Unexpected error: {str(exc)}"
                    logger.error("Unexpected error during lead enrichment: %s", last_error_msg)
                    return EnrichmentResult(status="failed", error=last_error_msg)

        return EnrichmentResult(
            status="failed",
            error=f"Enrichment failed after {max_attempts} attempts: {last_error_msg}",
        )


def get_enrichment_provider(
    mode: Optional[str] = None,
    transport: Optional[httpx.BaseTransport] = None,
) -> BaseEnrichmentProvider:
    """Factory to retrieve the active enrichment provider."""
    active_mode = (mode or settings.ENRICHMENT_MODE).lower()
    if active_mode == "off":
        return OffEnrichmentProvider()
    elif active_mode == "http":
        return HttpEnrichmentProvider(transport=transport)
    else:
        return MockEnrichmentProvider()
