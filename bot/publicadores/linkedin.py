"""LinkedIn con la API oficial (Posts API). Gratis.

Secretos necesarios:
    LINKEDIN_TOKEN   token OAuth con permiso w_member_social (perfil) o w_organization_social (página)
    LINKEDIN_AUTHOR  urn:li:person:XXXX (tu perfil) o urn:li:organization:XXXX (página de LicitaTIC)

Los carruseles se publican como documento PDF (el formato «deslizable» de LinkedIn)
cuando el Textos.md indica «documento: …»; si no, como publicación de varias imágenes.
"""
from __future__ import annotations

import io
import os
import re
from datetime import date

import requests
from PIL import Image

from .comun import ErrorPublicacion

API = "https://api.linkedin.com/rest"


def _version() -> str:
    """LinkedIn exige una versión AAAAMM reciente; usamos la de hace dos meses."""
    if os.environ.get("LINKEDIN_VERSION"):
        return os.environ["LINKEDIN_VERSION"]
    hoy = date.today()
    mes, anio = hoy.month - 2, hoy.year
    if mes <= 0:
        mes, anio = mes + 12, anio - 1
    return f"{anio}{mes:02d}"


def _cabeceras(extra: dict | None = None) -> dict:
    h = {
        "Authorization": f"Bearer {os.environ['LINKEDIN_TOKEN']}",
        "LinkedIn-Version": _version(),
        "X-Restli-Protocol-Version": "2.0.0",
    }
    h.update(extra or {})
    return h


def _post(ruta: str, json: dict) -> requests.Response:
    r = requests.post(f"{API}/{ruta}", headers=_cabeceras({"Content-Type": "application/json"}),
                      json=json, timeout=120)
    if r.status_code >= 400:
        raise ErrorPublicacion(f"LinkedIn {r.status_code}: {r.text}")
    return r


def _subir(url: str, datos: bytes) -> requests.Response:
    r = requests.put(url, data=datos, timeout=600,
                     headers={"Authorization": f"Bearer {os.environ['LINKEDIN_TOKEN']}"})
    if r.status_code >= 400:
        raise ErrorPublicacion(f"Subida a LinkedIn falló {r.status_code}: {r.text}")
    return r


def texto_linkedin(texto: str) -> str:
    """Formato «little text» de LinkedIn: escapa caracteres reservados y convierte #hashtags."""
    etiquetas = {}

    def guardar(m):
        clave = f"\x00{len(etiquetas)}\x00"
        etiquetas[clave] = "{hashtag|\\#|" + m.group(1) + "}"
        return clave

    t = re.sub(r"#(\w+)", guardar, texto)
    t = re.sub(r"([\\|{}@\[\]()<>#*_~])", r"\\\1", t)
    for k, v in etiquetas.items():
        t = t.replace(k, v)
    return t


def _imagen(autor: str, ruta) -> str:
    r = _post("images?action=initializeUpload", {"initializeUploadRequest": {"owner": autor}}).json()
    _subir(r["value"]["uploadUrl"], ruta.read_bytes())
    return r["value"]["image"]


def _documento(autor: str, imagenes) -> str:
    paginas = [Image.open(p).convert("RGB") for p in imagenes]
    buf = io.BytesIO()
    paginas[0].save(buf, "PDF", save_all=True, append_images=paginas[1:], resolution=150)
    r = _post("documents?action=initializeUpload", {"initializeUploadRequest": {"owner": autor}}).json()
    _subir(r["value"]["uploadUrl"], buf.getvalue())
    return r["value"]["document"]


def _video(autor: str, ruta) -> str:
    datos = ruta.read_bytes()
    r = _post("videos?action=initializeUpload", {"initializeUploadRequest": {
        "owner": autor, "fileSizeBytes": len(datos), "uploadCaptions": False, "uploadThumbnail": False,
    }}).json()["value"]
    partes = []
    for ins in r["uploadInstructions"]:
        trozo = datos[ins["firstByte"]: ins["lastByte"] + 1]
        resp = _subir(ins["uploadUrl"], trozo)
        partes.append(resp.headers.get("etag", "").strip('"'))
    _post("videos?action=finalizeUpload", {"finalizeUploadRequest": {
        "video": r["video"], "uploadToken": r.get("uploadToken", ""), "uploadedPartIds": partes}})
    return r["video"]


def publicar_linkedin(pub) -> str:
    autor = os.environ["LINKEDIN_AUTHOR"]
    if pub.tipo == "story":
        raise ErrorPublicacion("LinkedIn no tiene stories")
    if pub.tipo == "imagen":
        contenido = {"media": {"id": _imagen(autor, pub.medios[0])}}
    elif pub.tipo == "carrusel" and pub.titulo:
        contenido = {"media": {"title": pub.titulo, "id": _documento(autor, pub.medios)}}
    elif pub.tipo == "carrusel":
        contenido = {"multiImage": {"images": [{"id": _imagen(autor, m)} for m in pub.medios[:20]]}}
    elif pub.tipo == "video":
        contenido = {"media": {"id": _video(autor, pub.medios[0])}}
    else:
        raise ErrorPublicacion(f"Tipo no soportado en LinkedIn: {pub.tipo}")
    r = _post("posts", {
        "author": autor,
        "commentary": texto_linkedin(pub.texto),
        "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [],
                         "thirdPartyDistributionChannels": []},
        "content": contenido,
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    })
    return r.headers.get("x-restli-id", "ok")
