"""Informe semanal de métricas de Instagram y Facebook.

Uso:  python -m bot.metricas [--dias 7]
Escribe informes/AAAA-MM-DD.md y lo añade al resumen de GitHub Actions.
"""
from __future__ import annotations

import argparse
import os
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import requests

from .calendario import ZONA
from .publicadores.meta import GRAPH

RAIZ = Path(__file__).resolve().parents[1]
DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
TIPOS = {"REELS": "Reel", "CAROUSEL_ALBUM": "Carrusel", "IMAGE": "Imagen", "VIDEO": "Vídeo"}


def _get(ruta: str, **params) -> dict:
    params["access_token"] = os.environ["META_TOKEN"]
    r = requests.get(f"{GRAPH}/{ruta}", params=params, timeout=60)
    return r.json()


def _insights(mid: str) -> dict:
    for metricas in ("reach,saved,shares,views,total_interactions", "reach,saved,shares", "reach"):
        d = _get(f"{mid}/insights", metric=metricas)
        if "data" in d:
            return {x["name"]: x["values"][0]["value"] for x in d["data"]}
    return {}


def recoger(dias: int) -> tuple[dict, list[dict]]:
    ig = os.environ["META_IG_USER_ID"]
    cuenta = _get(ig, fields="username,followers_count,media_count")
    desde = datetime.now(ZONA) - timedelta(days=dias)
    posts, url = [], f"{ig}/media"
    params = {"fields": "id,caption,media_type,media_product_type,timestamp,like_count,comments_count,permalink",
              "limit": 50}
    d = _get(url, **params)
    for m in d.get("data", []):
        cuando = datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00")).astimezone(ZONA)
        if cuando < desde:
            continue
        m["cuando"] = cuando
        m["tipo"] = "Reel" if m.get("media_product_type") == "REELS" else TIPOS.get(m["media_type"], m["media_type"])
        m.update(_insights(m["id"]))
        posts.append(m)
    pagina = os.environ.get("META_PAGE_ID")
    if pagina:
        cuenta["facebook"] = _get(pagina, fields="name,followers_count,fan_count")
    return cuenta, posts


def informe(cuenta: dict, posts: list[dict], dias: int) -> str:
    hoy = datetime.now(ZONA)
    l = [f"# Informe LicitaTIC · {hoy:%d/%m/%Y}", "",
         f"Últimos {dias} días · Instagram @{cuenta.get('username', '?')}", ""]
    l.append(f"- **Seguidores Instagram:** {cuenta.get('followers_count', '?')}")
    fb = cuenta.get("facebook") or {}
    if fb:
        l.append(f"- **Seguidores Facebook:** {fb.get('followers_count', fb.get('fan_count', '?'))}")
    l.append(f"- **Publicaciones en el periodo:** {len(posts)}")
    if not posts:
        l += ["", "No hay publicaciones en este periodo."]
        return "\n".join(l) + "\n"

    alcance = sum(p.get("reach", 0) for p in posts)
    guardados = sum(p.get("saved", 0) for p in posts)
    compartidos = sum(p.get("shares", 0) for p in posts)
    likes = sum(p.get("like_count", 0) for p in posts)
    coments = sum(p.get("comments_count", 0) for p in posts)
    l += [f"- **Alcance total:** {alcance} · **Me gusta:** {likes} · **Comentarios:** {coments} · "
          f"**Guardados:** {guardados} · **Compartidos:** {compartidos}", ""]

    # Por tipo
    por_tipo = defaultdict(list)
    for p in posts:
        por_tipo[p["tipo"]].append(p)
    l += ["## Qué formato funciona mejor", "", "| Formato | Publicaciones | Alcance medio | Interacción media |",
          "|---|---|---|---|"]
    filas = []
    for t, ps in por_tipo.items():
        am = sum(p.get("reach", 0) for p in ps) / len(ps)
        im = sum(p.get("like_count", 0) + p.get("comments_count", 0) + p.get("saved", 0) + p.get("shares", 0)
                 for p in ps) / len(ps)
        filas.append((am, f"| {t} | {len(ps)} | {am:.0f} | {im:.1f} |"))
    l += [f for _, f in sorted(filas, reverse=True)]

    # Por hora
    por_hora = defaultdict(list)
    for p in posts:
        por_hora[f"{p['cuando']:%H}:00"].append(p.get("reach", 0))
    l += ["", "## Alcance medio por hora de publicación", "", "| Hora | Publicaciones | Alcance medio |",
          "|---|---|---|"]
    for h in sorted(por_hora):
        v = por_hora[h]
        l.append(f"| {h} | {len(v)} | {sum(v) / len(v):.0f} |")

    # Ranking
    l += ["", "## Top 5 publicaciones", "", "| Fecha | Formato | Alcance | ❤️ | 💬 | 📌 | ↗️ | Texto |",
          "|---|---|---|---|---|---|---|---|"]
    for p in sorted(posts, key=lambda p: p.get("reach", 0), reverse=True)[:5]:
        texto = (p.get("caption") or "").split("\n")[0][:60].replace("|", "/")
        l.append(f"| {DIAS[p['cuando'].weekday()]} {p['cuando']:%d/%m %H:%M} | {p['tipo']} | {p.get('reach', 0)} | {p.get('like_count', 0)} | "
                 f"{p.get('comments_count', 0)} | {p.get('saved', 0)} | {p.get('shares', 0)} | "
                 f"[{texto}]({p.get('permalink', '')}) |")

    mejor_tipo = max(filas)[1].split("|")[1].strip()
    mejor_hora = max(por_hora, key=lambda h: sum(por_hora[h]) / len(por_hora[h]))
    l += ["", "## Para la próxima semana", "",
          f"- El formato con más alcance medio ha sido **{mejor_tipo}**: dale más peso en el calendario.",
          f"- La franja con más alcance medio ha sido **{mejor_hora}**.",
          "- Repite el tema de la publicación con más guardados: es el contenido que tu público quiere conservar."]
    return "\n".join(l) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=7)
    args = ap.parse_args(argv)
    cuenta, posts = recoger(args.dias)
    texto = informe(cuenta, posts, args.dias)
    destino = RAIZ / "informes" / f"{datetime.now(ZONA):%Y-%m-%d}.md"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    print(texto)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(texto)


if __name__ == "__main__":
    main()
