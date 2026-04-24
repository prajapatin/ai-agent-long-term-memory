"""
Abstract LLM factory layer for LangChain agents.

Initializes and returns a LangChain chat model based on the LLM_PROVIDER
environment variable. Supports 'openai', 'groq', or 'ollama', swap
providers without touching agent code.
"""

import os

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()


def get_llm() -> BaseChatModel:
    """
    Factory function that returns a LangChain chat model based on LLM_PROVIDER.

    Environment Variables:
        LLM_PROVIDER: One of 'openai', 'groq', 'ollama' (default: 'openai')
        OPENAI_API_KEY: Required when LLM_PROVIDER=openai
        GROQ_API_KEY: Required when LLM_PROVIDER=groq
        OLLAMA_BASE_URL: Ollama server URL (default: http://localhost:11434)
        OLLAMA_MODEL: Ollama model name (default: llama3)

    Returns:
        A LangChain BaseChatModel instance.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        return ChatOpenAI(
            temperature=0,
            model="gpt-4.1-mini",
            api_key=api_key,
        )

    elif provider == "groq":
        from langchain_groq import ChatGroq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set.")
        return ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",
            api_key=api_key,
        )

    elif provider == "ollama":
        from langchain_ollama import ChatOllama

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3")
        return ChatOllama(
            temperature=0,
            model=model,
            base_url=base_url,
        )

    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: '{provider}'. "
            "Choose from: openai, groq, ollama"
        )
