"""Coleta de conteúdo textual de páginas de concorrentes (RF02, RF14, RNF05)."""

from __future__ import annotations

import time
import urllib.robotparser
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "GameTheoryAdvisorBot/1.0 (+trabalho academico SAG)"
REQUEST_TIMEOUT_SECONDS = 10
MIN_SECONDS_BETWEEN_REQUESTS = 1.0
MAX_CHARS = 8000

_last_request_at: float = 0.0


class ScrapingError(Exception):
    """Levantado quando a coleta falha e o chamador deve oferecer entrada manual (RF14)."""


@dataclass
class ScrapedPage:
    url: str
    text: str


def _respect_rate_limit() -> None:
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    if elapsed < MIN_SECONDS_BETWEEN_REQUESTS:
        time.sleep(MIN_SECONDS_BETWEEN_REQUESTS - elapsed)
    _last_request_at = time.monotonic()


def _is_allowed_by_robots(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except OSError:
        # robots.txt indisponível/ilegível: não bloqueia a coleta, mas não
        # temos como confirmar a permissão explicitamente.
        return True
    return parser.can_fetch(USER_AGENT, url)


def fetch_page_text(url: str) -> ScrapedPage:
    """Baixa e limpa o texto visível de uma página pública estática.

    Levanta ScrapingError em qualquer falha (rede, bloqueio, robots.txt,
    conteúdo vazio) para que a camada de chat ofereça o fallback manual (RF14).
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ScrapingError(f"URL inválida: {url}")

    if not _is_allowed_by_robots(url):
        raise ScrapingError(
            f"O robots.txt de {parsed.netloc} não permite a coleta desta página."
        )

    _respect_rate_limit()

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ScrapingError(f"Falha ao acessar {url}: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        tag.decompose()

    text = " ".join(soup.get_text(separator=" ").split())
    if not text:
        raise ScrapingError(
            f"Nenhum texto legível encontrado em {url} "
            "(possivelmente depende de JavaScript)."
        )

    return ScrapedPage(url=url, text=text[:MAX_CHARS])
