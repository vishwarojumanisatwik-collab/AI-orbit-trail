from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GeneratedDescription(BaseModel):
    """Validated LLM-generated description for an AI tool."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str = ""
    source_quality: str
    generated_by: str = "openai"
    model: str
    description_generated: bool = False

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()

        # Empty is allowed for records with unavailable evidence.
        if not value:
            return ""

        # Keep descriptions concise for the final directory.
        if len(value) > 500:
            raise ValueError(
                "Description exceeds the 500-character limit."
            )

        # Avoid multi-paragraph output.
        if "\n" in value:
            raise ValueError(
                "Description must be a single paragraph."
            )

        # Basic promotional-language quality gate.
        banned_phrases = [
            "best",
            "number one",
            "#1",
            "revolutionary",
            "game-changing",
            "world-class",
            "unmatched",
            "ultimate",
        ]

        lowered = value.lower()

        for phrase in banned_phrases:
            if phrase in lowered:
                raise ValueError(
                    f"Promotional phrase detected: '{phrase}'."
                )

        return value