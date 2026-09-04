from __future__ import annotations


OFFICIAL_DESCRIPTION_FALLBACKS: dict[str, dict[str, str]] = {
    "AltNotes": {
        "description": (
            "AI voice notes app for recording, transcribing, and summarizing "
            "audio, with AI-powered search and question answering across saved notes."
        ),
        "source": "official_website",
        "source_url": "https://getaltnotes.com/",
    },
    "ChatGPT": {
        "description": (
            "Conversational AI assistant for tasks such as answering questions, "
            "writing, studying, planning, coding, and analyzing information."
        ),
        "source": "official_openai_documentation",
        "source_url": "https://help.openai.com/en/articles/12677804-what-is-chatgpt-faq",
    },
}