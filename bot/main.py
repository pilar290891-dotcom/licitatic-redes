"""Bot de publicación de LicitaTIC.

Uso:
    python -m bot.main listar [--dias 7]      muestra lo que se va a publicar
    python -m bot.main publicar               publica lo que toca ahora (lo lanza GitHub Actions)

Por seguridad, «publicar» solo simula salvo que la variable PUBLICAR valga «si».
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path

from .calendario import ZONA, construir_calendario

RAIZ = Path(__file__).resolve().parents[1]
ESTADO = RAIZ / "bot" / "estado" / "publicados.json"
MAX_INTENTOS = 3

SECRETOS = {
    "instagram": ["META_TOKEN", "META_IG_USER_ID"],
    "facebook": ["META_TOKEN", "META_PAGE_ID"],
    "linkedin": ["LINKEDIN_TOKEN", "LINKEDIN_AUTHOR"],
    "tiktok": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"],
}


def redes_activas() -> set[str]:
    elegidas = os.environ.get("REDES", "instagram,facebook,linkedin,tiktok")
    pedidas = {r.strip() for r in elegidas.split(",") if r.strip()}
    return {r for r in pedidas if all(os.environ.get(s) for s in SECRETOS.get(r, ["?"]))}


def cargar_estado() -> dict:
    if ESTADO.exists():
        return json.loads(ESTADO.read_text(encoding="utf-8"))
    return {}


def guardar_estado(estado: dict):
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")


def publicador(red: str):
    if red == "instagram":
        from .publicadores.meta import publicar_instagram
        return publicar_instagram
    if red == "facebook":
        from .publicadores.meta import publicar_facebook
        return publicar_facebook
    if red == "linkedin":
        from .publicadores.linkedin import publicar_linkedin
        return publicar_linkedin
    if red == "tiktok":
        from .publicadores.tiktok import publicar_tiktok
        return publicar_tiktok
    raise ValueError(red)


def listar(dias: int):
    ahora = datetime.now(ZONA)
    hasta = ahora + timedelta(days=dias)
    estado = cargar_estado()
    activas = redes_activas()
    print(f"Redes conectadas: {', '.join(sorted(activas)) or 'ninguna todavía'}\n")
    for p in construir_calendario(RAIZ):
        if ahora - timedelta(hours=12) <= p.cuando <= hasta:
            marca = "✓" if estado.get(p.id, {}).get("ok") else " "
            aviso = f"  ⚠ {', '.join(p.avisos)}" if p.avisos else ""
            print(f"[{marca}] {p.resumen()}{aviso}")


def publicar():
    simular = os.environ.get("PUBLICAR", "no").lower() not in ("si", "sí", "yes", "true", "1")
    ventana = timedelta(hours=float(os.environ.get("VENTANA_HORAS", "3")))
    ahora = datetime.now(ZONA)
    estado = cargar_estado()
    activas = redes_activas()
    informe = [f"## Publicaciones {ahora:%d/%m/%Y %H:%M} ({'SIMULACIÓN' if simular else 'REAL'})", ""]
    if not activas:
        informe.append("Ninguna red conectada todavía: faltan los secretos (ver bot/README.md).")

    pendientes = [p for p in construir_calendario(RAIZ)
                  if p.cuando <= ahora and ahora - p.cuando <= ventana
                  and not estado.get(p.id, {}).get("ok")
                  and estado.get(p.id, {}).get("intentos", 0) < MAX_INTENTOS]

    fallos = 0
    for p in pendientes:
        if p.red not in activas:
            continue
        if simular:
            informe.append(f"- (simulado) {p.resumen()}")
            continue
        registro = estado.setdefault(p.id, {"intentos": 0})
        registro["intentos"] += 1
        try:
            resultado = publicador(p.red)(p)
            registro.update(ok=True, id_red=str(resultado), publicado=ahora.isoformat())
            registro.pop("error", None)
            informe.append(f"- ✅ {p.resumen()}")
        except Exception as e:  # noqa: BLE001 — seguimos con el resto de redes
            fallos += 1
            registro["error"] = str(e)[:500]
            informe.append(f"- ❌ {p.resumen()}\n  `{str(e)[:300]}`")
            traceback.print_exc()
        guardar_estado(estado)

    if len(informe) == 2:
        informe.append("Nada que publicar en este momento.")
    texto = "\n".join(informe)
    print(texto)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(texto + "\n")
    return 1 if fallos else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Bot de publicación de LicitaTIC")
    sub = ap.add_subparsers(dest="orden", required=True)
    l = sub.add_parser("listar")
    l.add_argument("--dias", type=int, default=7)
    sub.add_parser("publicar")
    args = ap.parse_args(argv)
    if args.orden == "listar":
        listar(args.dias)
        return 0
    return publicar()


if __name__ == "__main__":
    sys.exit(main())
