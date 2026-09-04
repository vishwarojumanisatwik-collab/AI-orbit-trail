from __future__ import annotations

from typing import Any

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from src.config import LLM_DRY_RUN, LLM_MODEL
from src.enrichment.description_models import GeneratedDescription
from src.enrichment.description_prompt import (
    SYSTEM_PROMPT,
    build_description_prompt,
)


def _is_retryable_error(exception: BaseException) -> bool:
    """Return True only for errors that may succeed on retry."""

    if isinstance(
        exception,
        (
            APIConnectionError,
            APITimeoutError,
            InternalServerError,
        ),
    ):
        return True

    # Rate limits can be temporary, but insufficient quota is not.
    if isinstance(exception, RateLimitError):
        error_code = getattr(exception, "code", None)

        if error_code == "insufficient_quota":
            return False

        return True

    return False


class DescriptionGenerator:
    """Generate and validate factual tool descriptions using an LLM."""

    def __init__(self) -> None:
        self.model = LLM_MODEL
        self.client = None if LLM_DRY_RUN else OpenAI()

    @retry(
        retry=retry_if_exception(_is_retryable_error),
        wait=wait_exponential(
            multiplier=1,
            min=2,
            max=20,
        ),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with retries for transient failures."""

        response = self.client.responses.create(
            model=self.model,
            instructions=SYSTEM_PROMPT,
            input=prompt,
        )

        return response.output_text.strip()

    def generate(self, record: dict[str, Any]) -> GeneratedDescription:
        name = record["name"]
        source_quality = record["source_quality"]

        # Never invent a description when evidence is unavailable.
        if source_quality == "unavailable":
            return GeneratedDescription(
                name=name,
                description="",
                source_quality=source_quality,
                model=self.model,
                description_generated=False,
            )

        # Dry-run mode avoids all API calls.
        if LLM_DRY_RUN:
            return GeneratedDescription(
        name=name,
        description="",
        source_quality=source_quality,
        model=self.model,
        description_generated=False,
    )

        prompt = build_description_prompt(record)

        description = self._call_llm(prompt)

        # Pydantic performs the final quality validation.
        return GeneratedDescription(
            name=name,
            description=description,
            source_quality=source_quality,
            model=self.model,
            description_generated=True,
        )