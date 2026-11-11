"""Instagram y Facebook con la API oficial de Meta (Graph API). Gratis.

Secretos necesarios:
    META_TOKEN       token de página de larga duración (no caduca si se genera desde un token de usuario largo)
    META_PAGE_ID     id de la página de Facebook de LicitaTIC
    META_IG_USER_ID  id de la cuenta profesional de Instagram vinculada a esa página
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import requests

from .comun import ErrorPublicacion, url_publica

VERSION = "v21.0"
GRAPH = f"https://graph.facebook.com/{VERSION}"
RUPLOAD = f"https://rupload.facebook.com/ig-api-upload/{VERSION}"


def _token() -> str:
    return os.environ["META_TOKEN"]


def _pedir(metodo: str, url: str, **kw) -> dict:
    kw.setdefault("timeout", 120)
    params = kw.pop("params", {}) or {}
    params.setdefault("access_token", _token())
    r = requests.request(metodo, url, params=params, **kw)
    datos = r.json() if r.content else {}
    if r.status_code >= 400 or "error" in datos:
        raise ErrorPublicacion(f"Meta {r.status_code}: {datos.get('error', r.text)}")
    return datos


# ------------------------------------------------------------------ Instagram

def _esperar_contenedor(cid: str, maximo: int = 600):
    inicio = time.time()
    while time.time() - inicio < maximo:
        estado = _pedir("GET", f"{GRAPH}/{cid}", params={"fields": "status_code,status"})
        codigo = estado.get("status_code")
        if codigo == "FINISHED":
            return
        if codigo in ("ERROR", "EXPIRED"):
            raise ErrorPublicacion(f"Instagram no pudo procesar el archivo: {estado.get('status')}")
        time.sleep(5)
    raise ErrorPublicacion("Instagram tardó demasiado en procesar el archivo")


def _subir_video_ig(ig: str, video: Path, **campos) -> str:
    """Contenedor de vídeo con subida directa del archivo (no hace falta alojarlo fuera)."""
    cont = _pedir("POST", f"{GRAPH}/{ig}/media", data={"upload_type": "resumable", **campos})
    cid = cont["id"]
    datos = video.read_bytes()
    r = requests.post(
        f"{RUPLOAD}/{cid}",
        headers={"Authorization": f"OAuth {_token()}", "offset": "0", "file_size": str(len(datos))},
        data=datos, timeout=600,
    )
    if r.status_code >= 400:
        raise ErrorPublicacion(f"Subida de vídeo a Instagram falló: {r.text}")
    return cid


def publicar_instagram(pub) -> str:
    ig = os.environ["META_IG_USER_ID"]
    if pub.tipo == "imagen":
        cid = _pedir("POST", f"{GRAPH}/{ig}/media",
                     data={"image_url": url_publica(pub.medios[0]), "caption": pub.texto})["id"]
    elif pub.tipo == "carrusel":
        hijos = []
        for m in pub.medios[:10]:
            h = _pedir("POST", f"{GRAPH}/{ig}/media",
                       data={"image_url": url_publica(m), "is_carousel_item": "true"})["id"]
            hijos.append(h)
        for h in hijos:
            _esperar_contenedor(h)
        cid = _pedir("POST", f"{GRAPH}/{ig}/media", data={
            "media_type": "CAROUSEL", "children": ",".join(hijos), "caption": pub.texto})["id"]
    elif pub.tipo == "video":
        campos = {"media_type": "REELS", "caption": pub.texto, "share_to_feed": "true"}
        if pub.portada:
            campos["cover_url"] = url_publica(pub.portada)
        cid = _subir_video_ig(ig, pub.medios[0], **campos)
    elif pub.tipo == "story":
        cid = _pedir("POST", f"{GRAPH}/{ig}/media",
                     data={"media_type": "STORIES", "image_url": url_publica(pub.medios[0])})["id"]
    else:
        raise ErrorPublicacion(f"Tipo no soportado en Instagram: {pub.tipo}")
    _esperar_contenedor(cid)
    return _pedir("POST", f"{GRAPH}/{ig}/media_publish", data={"creation_id": cid})["id"]


# ------------------------------------------------------------------ Facebook

def publicar_facebook(pub) -> str:
    page = os.environ["META_PAGE_ID"]
    if pub.tipo == "imagen":
        return _pedir("POST", f"{GRAPH}/{page}/photos",
                      data={"url": url_publica(pub.medios[0]), "message": pub.texto})["id"]
    if pub.tipo == "carrusel":
        fotos = [_pedir("POST", f"{GRAPH}/{page}/photos",
                        data={"url": url_publica(m), "published": "false"})["id"] for m in pub.medios]
        datos = {"message": pub.texto}
        for i, f in enumerate(fotos):
            datos[f"attached_media[{i}]"] = f'{{"media_fbid":"{f}"}}'
        return _pedir("POST", f"{GRAPH}/{page}/feed", data=datos)["id"]
    if pub.tipo == "video":
        inicio = _pedir("POST", f"{GRAPH}/{page}/video_reels", data={"upload_phase": "start"})
        vid = inicio["video_id"]
        datos = pub.medios[0].read_bytes()
        r = requests.post(inicio["upload_url"], data=datos, timeout=600, headers={
            "Authorization": f"OAuth {_token()}", "offset": "0", "file_size": str(len(datos))})
        if r.status_code >= 400:
            raise ErrorPublicacion(f"Subida de reel a Facebook falló: {r.text}")
        _pedir("POST", f"{GRAPH}/{page}/video_reels", data={
            "upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
            "description": pub.texto})
        return vid
    if pub.tipo == "story":
        foto = _pedir("POST", f"{GRAPH}/{page}/photos",
                      data={"url": url_publica(pub.medios[0]), "published": "false"})["id"]
        return _pedir("POST", f"{GRAPH}/{page}/photo_stories", data={"photo_id": foto})["post_id"]
    raise ErrorPublicacion(f"Tipo no soportado en Facebook: {pub.tipo}")


# ------------------------------------------------------------------ métricas

def metricas_instagram(desde_dias: int = 7) -> list[dict]:
    ig = os.environ["META_IG_USER_ID"]
    medios = _pedir("GET", f"{GRAPH}/{ig}/media", params={
        "fields": "id,caption,media_type,media_product_type,timestamp,like_count,comments_count,permalink",
        "limit": 50}).get("data", [])
    resultado = []
    for m in medios:
        try:
            ins = _pedir("GET", f"{GRAPH}/{m['id']}/insights",
                         params={"metric": "reach,saved,shares,views"}).get("data", [])
            for x in ins:
                m[x["name"]] = x["values"][0]["value"]
        except ErrorPublicacion:
            pass
        resultado.append(m)
    return resultado
