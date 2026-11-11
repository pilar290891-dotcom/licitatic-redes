"""TikTok con la Content Posting API oficial. Gratis.

Secretos necesarios:
    TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET   de tu app en developers.tiktok.com
    TIKTOK_REFRESH_TOKEN                      se obtiene una vez al autorizar la app (dura 1 año)

Variables opcionales:
    TIKTOK_PRIVACIDAD   SELF_ONLY (por defecto) hasta que TikTok apruebe la auditoría de la app;
                        después, PUBLIC_TO_EVERYONE.

Limitaciones de TikTok:
  * Sin auditoría aprobada, todo lo publicado queda en privado («solo yo»).
  * Los carruseles de fotos solo se pueden enviar desde una URL de un dominio verificado
    en la app (por ejemplo, licitatic.es). Configura BASE_URL_MEDIOS con ese dominio.
"""
from __future__ import annotations

import os
import time

import requests

from .comun import ErrorPublicacion, url_publica

API = "https://open.tiktokapis.com/v2"
_token_cache: dict[str, str] = {}


def _token() -> str:
    if "t" in _token_cache:
        return _token_cache["t"]
    r = requests.post(f"{API}/oauth/token/", timeout=60, data={
        "client_key": os.environ["TIKTOK_CLIENT_KEY"],
        "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
        "grant_type": "refresh_token",
        "refresh_token": os.environ["TIKTOK_REFRESH_TOKEN"],
    })
    datos = r.json()
    if "access_token" not in datos:
        raise ErrorPublicacion(f"TikTok no renovó el token: {datos}")
    _token_cache["t"] = datos["access_token"]
    return datos["access_token"]


def _post(ruta: str, json: dict) -> dict:
    r = requests.post(f"{API}/{ruta}", json=json, timeout=120, headers={
        "Authorization": f"Bearer {_token()}", "Content-Type": "application/json; charset=UTF-8"})
    datos = r.json()
    if datos.get("error", {}).get("code", "ok") != "ok":
        raise ErrorPublicacion(f"TikTok: {datos['error']}")
    return datos.get("data", {})


def _privacidad() -> str:
    return os.environ.get("TIKTOK_PRIVACIDAD", "SELF_ONLY")


def _esperar(publish_id: str, maximo: int = 300) -> str:
    inicio = time.time()
    while time.time() - inicio < maximo:
        d = _post("post/publish/status/fetch/", {"publish_id": publish_id})
        estado = d.get("status")
        if estado == "PUBLISH_COMPLETE":
            return publish_id
        if estado == "FAILED":
            raise ErrorPublicacion(f"TikTok rechazó la publicación: {d.get('fail_reason')}")
        time.sleep(5)
    return publish_id  # sigue procesándose; TikTok la terminará solo


def publicar_tiktok(pub) -> str:
    if pub.tipo == "story":
        raise ErrorPublicacion("No se publican stories en TikTok")
    if pub.tipo == "video":
        datos = pub.medios[0].read_bytes()
        d = _post("post/publish/video/init/", {
            "post_info": {"title": pub.texto[:2200], "privacy_level": _privacidad(),
                          "disable_comment": False, "disable_duet": False, "disable_stitch": False},
            "source_info": {"source": "FILE_UPLOAD", "video_size": len(datos),
                            "chunk_size": len(datos), "total_chunk_count": 1},
        })
        r = requests.put(d["upload_url"], data=datos, timeout=600, headers={
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{len(datos) - 1}/{len(datos)}"})
        if r.status_code >= 400:
            raise ErrorPublicacion(f"Subida de vídeo a TikTok falló: {r.text}")
        return _esperar(d["publish_id"])
    # imagen o carrusel → publicación de fotos
    d = _post("post/publish/content/init/", {
        "post_info": {"title": (pub.titulo or pub.texto)[:90], "description": pub.texto[:4000],
                      "privacy_level": _privacidad(), "disable_comment": False, "auto_add_music": True},
        "source_info": {"source": "PULL_FROM_URL", "photo_cover_index": 0,
                        "photo_images": [url_publica(m) for m in pub.medios[:35]]},
        "post_mode": "DIRECT_POST",
        "media_type": "PHOTO",
    })
    return _esperar(d["publish_id"])
