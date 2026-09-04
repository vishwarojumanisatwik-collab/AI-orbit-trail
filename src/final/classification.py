from __future__ import annotations

import re


CATEGORY_RULES: list[tuple[str, list[str]]] = [
    (
        "AI Coding",
        [
            "coding",
            "code",
            "developer",
            "programming",
            "software development",
            "ide",
            "repository",
            "software engineering",
        ],
    ),
    (
        "AI Productivity",
        [
            "productivity",
            "workflow",
            "automation",
            "scheduling",
            "calendar",
            "task management",
            "daily coach",
            "planning",
        ],
    ),
    (
        "AI Research",
        [
            "research",
            "user research",
            "analysis",
            "analytics",
            "researching",
        ],
    ),
    (
        "AI Image",
        [
            "image",
            "photo",
            "visual",
            "manga",
            "anime",
            "image enhancement",
            "photo enhancement",
            "image generator",
        ],
    ),
    (
        "AI Video",
        [
            "video",
            "whiteboard",
            "explainer video",
            "video generation",
        ],
    ),
    (
        "AI Audio",
        [
            "audio",
            "voice",
            "music",
            "song",
            "transcription",
            "speech",
            "voice notes",
        ],
    ),
    (
        "AI Finance",
        [
            "finance",
            "financial",
            "stock",
            "portfolio",
            "trading",
            "invest",
            "investment",
        ],
    ),
    (
        "AI Cybersecurity",
        [
            "cybersecurity",
            "security",
            "threat detection",
            "incident response",
            "attack surface",
            "cyber security",
        ],
    ),
    (
        "AI Business",
        [
            "business",
            "ecommerce",
            "e-commerce",
            "founders",
            "customers",
            "clients",
            "venture",
            "company",
            "companies",
        ],
    ),
    (
        "AI Agents",
        [
            "agent",
            "agents",
            "agentic",
            "ai agent",
            "ai agents",
        ],
    ),
    (
        "AI Notes",
        [
            "notes",
            "note-taking",
            "meeting notes",
            "voice notes",
            "note app",
        ],
    ),
    (
        "AI Models",
        [
            "model",
            "models",
            "foundation model",
            "large language model",
            "llm",
            "open-source model",
            "open source model",
            "fine-tune",
            "fine tuning",
            "fine-tuning",
            "serve models",
            "trained on your data",
            "deepseek",
            "language model",
        ],
    ),
    (
        "AI APIs",
        [
            "api",
            "apis",
            "api access",
            "developer api",
            "model api",
        ],
    ),
]


def _normalize(text: str) -> str:
    """Normalize text for reliable keyword matching."""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def classify_tool(
    name: str,
    description: str = "",
    headings: list[str] | None = None,
) -> list[str]:
    """
    Classify an AI tool using its name, description, and official
    website headings.

    Multiple categories are allowed when the evidence supports them.
    """

    headings = headings or []

    evidence = " ".join(
        [
            name,
            description,
            *headings,
        ]
    )

    evidence = _normalize(evidence)

    categories: list[str] = []

    for category, keywords in CATEGORY_RULES:
        for keyword in keywords:
            keyword_normalized = _normalize(keyword)

            if keyword_normalized in evidence:
                categories.append(category)
                break

    return categories