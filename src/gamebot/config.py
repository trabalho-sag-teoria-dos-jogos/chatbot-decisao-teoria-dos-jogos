"""Carregamento de configuração via variáveis de ambiente (RNF04)."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_MODEL_FALLBACK = os.environ.get("GROQ_MODEL_FALLBACK", "llama-3.1-8b-instant")
# Modelo com suporte a imagem (RF02/RF14 — fallback quando o link do
# concorrente está bloqueado e o usuário manda um print da página).
GROQ_VISION_MODEL = os.environ.get("GROQ_VISION_MODEL", "qwen/qwen3.6-27b")
# Sistema "Compound" da Groq — usa busca na internet (Tavily) e visita de
# site de verdade, para quando o usuário só sabe o NOME do concorrente,
# não o link (RF02).
GROQ_COMPOUND_MODEL = os.environ.get("GROQ_COMPOUND_MODEL", "groq/compound")


def require_groq_api_key() -> str:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY não configurada. Defina-a em um arquivo .env "
            "(veja .env.example)."
        )
    return GROQ_API_KEY
