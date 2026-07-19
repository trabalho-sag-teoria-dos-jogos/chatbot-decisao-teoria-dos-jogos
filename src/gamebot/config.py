"""Carregamento de configuração via variáveis de ambiente (RNF04)."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_MODEL_FALLBACK = os.environ.get("GROQ_MODEL_FALLBACK", "llama-3.1-8b-instant")


def require_groq_api_key() -> str:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY não configurada. Defina-a em um arquivo .env "
            "(veja .env.example)."
        )
    return GROQ_API_KEY
