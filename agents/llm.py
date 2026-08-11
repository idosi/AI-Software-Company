"""Single place to build the LLM client used by every agent."""

import os

from langchain_anthropic import ChatAnthropic

DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")


def get_llm(temperature: float = 0.2) -> ChatAnthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    return ChatAnthropic(
        model=DEFAULT_MODEL, 
        api_key=api_key
    )
