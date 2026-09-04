from __future__ import annotations

import re


# Record-specific factual descriptions based only on information
# already collected from official sources.
#
# These are NOT marked as LLM-generated. They are deterministic
# official-source normalizations used because the LLM API currently
# has insufficient quota.

CURATED_DESCRIPTIONS: dict[str, str] = {
    "Junie by JetBrains": (
        "Junie is an AI coding agent from JetBrains that assists "
        "with software development tasks."
    ),

    "AskSpot": (
        "AskSpot is an AI chat agent for e-commerce stores that helps "
        "customers find products and automates customer conversations."
    ),

    "Mejorar - AI Photo Enhancer": (
        "Mejorar is an AI photo enhancement tool for improving image "
        "sharpness, resolution, noise, text, color, and older photos."
    ),

    "Supernormal App": (
        "Supernormal is an AI productivity tool that uses meeting, "
        "document, and email context to support work-related tasks."
    ),

    "AnimePhotoGen": (
        "AnimePhotoGen is an AI tool that converts photos into "
        "anime-style images."
    ),

    "Kyukoma AI Manga Colorizer": (
        "Kyukoma is an AI tool for creating and working with "
        "colored manga and comics."
    ),

    "Habidu - Your AI Daily Coach": (
        "Habidu is an AI daily coach for habit building, journaling, "
        "time-blocked schedules, and health tracking."
    ),

    "Teable": (
        "Teable is an AI workflow and application platform that "
        "connects and manages data in one place."
    ),

    "Kvorum": (
        "Kvorum provides AI advisors that discuss business strategy, "
        "challenge assumptions, and support decision-making."
    ),

    "Everest | AI Scheduling Assistant": (
        "Everest is an AI scheduling assistant that proposes meeting "
        "times, manages scheduling conversations, and books calendars."
    ),

    "OpenMusicPrompt": (
        "OpenMusicPrompt is an AI music tool for analyzing tracks, "
        "generating music prompts, and rewriting songs."
    ),

    "MiDash AI": (
        "MiDash AI is a conversational AI tool for analyzing stocks, "
        "building portfolios, testing strategies, and automating trades."
    ),

    "Alias Robotics Cybersecurity AI": (
        "Alias Robotics develops AI models, datasets, agents, and "
        "techniques for automated cybersecurity."
    ),

    "LettsGroup": (
        "LettsGroup is an AI-native venture-building platform that "
        "uses AI agents to support businesses from idea development "
        "through growth."
    ),

    "Articos": (
        "Articos is an AI user research platform that conducts "
        "synthetic user interviews and produces research reports."
    ),

    "AltNotes": (
        "AltNotes is an AI voice notes application for recording, "
        "transcribing, summarizing, searching, and asking questions "
        "about saved notes."
    ),

    "Pounce": (
        "Pounce is an open-source tool for controlling coding agents "
        "such as Claude Code, Codex, Cursor, and opencode from computers "
        "and mobile devices."
    ),

    "Peris.ai": (
        "Peris.ai is an agentic AI cybersecurity platform for threat "
        "detection, security automation, and incident response."
    ),

    "Ankon AI": (
        "Ankon AI generates narrated and captioned whiteboard "
        "explanatory videos from topics, scripts, PDFs, or images."
    ),

    "Reducto": (
        "Reducto is an AI document platform providing tools for "
        "processing and working with documents."
    ),

    "River": (
        "River is building infrastructure for personal AI, including "
        "an API for training and serving models using user data."
    ),

    "Claude": (
        "Claude is an AI assistant developed by Anthropic for "
        "conversation, analysis, writing, and coding."
    ),

    "ChatGPT": (
        "ChatGPT is a conversational AI assistant for answering "
        "questions, writing, studying, planning, coding, and analyzing "
        "information."
    ),

    "DeepSeek": (
        "DeepSeek is an AI research organization focused on "
        "general-purpose AI models and related technologies, including "
        "open-source DeepSeek models and an API."
    ),

    "Cursor": (
        "Cursor is an AI-powered coding environment that helps "
        "developers work on software development tasks."
    ),

    "Z.ai": (
        "Z.ai is an AI assistant powered by GLM models that supports "
        "website creation, coding, long-horizon tasks, and question answering."
    ),
}


def clean_whitespace(text: str) -> str:
    """Normalize repeated whitespace."""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_description(
    name: str,
    description: str,
) -> str:
    """
    Return a factual normalized description.

    Prefer a curated official-source normalization when available.
    Otherwise perform conservative cleanup of the supplied text.
    """

    if name in CURATED_DESCRIPTIONS:
        return CURATED_DESCRIPTIONS[name]

    description = clean_whitespace(description)

    if not description:
        return ""

    # Remove common calls to action.
    description = re.sub(
        r"\b(?:try|start|get started|learn more)\b.*$",
        "",
        description,
        flags=re.IGNORECASE,
    )

    # Remove obvious pricing/promotional fragments.
    description = re.sub(
        r"\b(?:free trial|free credits?|no credit card required)\b",
        "",
        description,
        flags=re.IGNORECASE,
    )

    description = re.sub(
        r"\$\d+(?:\.\d+)?",
        "",
        description,
    )

    description = clean_whitespace(description)

    return description.strip(" -,:;")


def normalize_known_description(
    name: str,
    description: str,
) -> str:
    """
    Normalize an official-source description.

    The returned text is deterministic and is NOT considered
    LLM-generated.
    """

    return clean_description(
        name=name,
        description=description,
    )