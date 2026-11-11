from __future__ import annotations

import os
import subprocess
from urllib.parse import quote
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


class ErrorPublicacion(Exception):
    pass


def _commit_actual() -> str:
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        return sha
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=RAIZ, text=True).strip()
    except Exception:
        return "main"


def url_publica(ruta: Path) -> str:
    """URL pública del archivo en el repositorio (debe ser público para que Meta/TikTok la descarguen).

    Se fija al commit actual para que el enlace no cambie aunque el agente suba más contenido.
    BASE_URL_MEDIOS permite usar otro alojamiento (por ejemplo, un dominio propio).
    """
    rel = quote(Path(ruta).resolve().relative_to(RAIZ).as_posix())
    base = os.environ.get("BASE_URL_MEDIOS")
    if base:
        return f"{base.rstrip('/')}/{rel}"
    repo = os.environ.get("GITHUB_REPOSITORY", "pilar290891-dotcom/licitatic-redes")
    return f"https://raw.githubusercontent.com/{repo}/{_commit_actual()}/{rel}"
