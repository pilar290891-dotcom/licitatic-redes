"""Lee las carpetas que prepara el agente de contenido y construye el calendario de publicaciones.

Estructura esperada de cada día (la que ya usa el agente):

    semana-XX-YY/N_Dia_DD/
        Textos.md                      # horario + copys por red
        1_Instagram_y_Facebook/HHMM_*.jpg
        2_TikTok/HHMM_*.jpg
        3_LinkedIn/HHMM_*.jpg
        4_Stories/HHMM_*.jpg
        5_Reel/HHMM_reel.mp4 (+ portada_reel.jpg)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

ZONA = ZoneInfo("Europe/Madrid")

CARPETAS_RED = {
    "1_Instagram_y_Facebook": ("instagram", "facebook"),
    "2_TikTok": ("tiktok",),
    "3_LinkedIn": ("linkedin",),
}
EXT_IMAGEN = {".jpg", ".jpeg", ".png"}
EXT_VIDEO = {".mp4", ".mov"}


@dataclass
class Publicacion:
    id: str                      # único y estable: AAAA-MM-DD_HHMM_red_tipo
    cuando: datetime
    red: str                     # instagram | facebook | tiktok | linkedin
    tipo: str                    # imagen | carrusel | video | story
    medios: list[Path]
    texto: str = ""
    titulo: str = ""             # título TikTok / documento LinkedIn
    portada: Path | None = None
    avisos: list[str] = field(default_factory=list)

    def resumen(self) -> str:
        t = self.texto.replace("\n", " ")[:60]
        return (f"{self.cuando:%a %d/%m %H:%M} {self.red:9} {self.tipo:8} "
                f"{len(self.medios)} archivo(s) | {t}")


# ---------------------------------------------------------------- Textos.md

def _red_de_cabecera(cabecera: str) -> set[str]:
    c = cabecera.lower()
    redes = set()
    if "ig" in re.findall(r"\b\w+\b", c) or "instagram" in c:
        redes.add("instagram")
    if "fb" in re.findall(r"\b\w+\b", c) or "facebook" in c:
        redes.add("facebook")
    if "tiktok" in c:
        redes.add("tiktok")
    if "linkedin" in c:
        redes.add("linkedin")
    return redes


def leer_textos(ruta: Path) -> tuple[date | None, dict[str, dict[str, dict]]]:
    """Devuelve (fecha, {"HHMM": {red: {"texto", "titulo"}}})."""
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    fecha = None
    m = re.search(r"(\d{1,2})/(\d{1,2})", lineas[0] if lineas else "")
    if m:
        fecha = _fecha_cercana(int(m.group(1)), int(m.group(2)))

    textos: dict[str, dict[str, dict]] = {}
    hora = None
    redes_actuales: set[str] = set()
    titulo = ""
    buffer: list[str] = []

    def volcar():
        if hora and redes_actuales:
            cuerpo = "\n".join(buffer).strip()
            for r in redes_actuales:
                textos.setdefault(hora, {})[r] = {"texto": cuerpo, "titulo": titulo}

    for linea in lineas[1:]:
        sec = re.match(r"^##\s+(\d{1,2}):(\d{2})", linea)
        if linea.startswith("## "):
            volcar()
            hora = f"{int(sec.group(1)):02d}{sec.group(2)}" if sec else None
            redes_actuales, titulo, buffer = set(), "", []
            continue
        cab = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", linea)
        if cab and hora and _red_de_cabecera(cab.group(1)):
            volcar()
            redes_actuales = _red_de_cabecera(cab.group(1))
            extra = cab.group(1) + " " + cab.group(2)
            t = re.search(r"\((?:título|titulo|documento):\s*([^)]+)\)", extra, re.I)
            titulo = t.group(1).strip() if t else ""
            buffer = []
            continue
        if hora:
            buffer.append(linea)
    volcar()
    return fecha, textos


def _fecha_cercana(dia: int, mes: int, hoy: date | None = None) -> date:
    """El Textos.md no lleva año: se elige el año que deja la fecha más cerca de hoy."""
    hoy = hoy or datetime.now(ZONA).date()
    candidatas = []
    for anio in (hoy.year - 1, hoy.year, hoy.year + 1):
        try:
            candidatas.append(date(anio, mes, dia))
        except ValueError:
            pass
    return min(candidatas, key=lambda d: abs((d - hoy).days))


# ---------------------------------------------------------------- medios

def _agrupar_por_hora(carpeta: Path) -> dict[str, list[Path]]:
    grupos: dict[str, list[Path]] = {}
    if not carpeta.is_dir():
        return grupos
    for f in carpeta.iterdir():
        m = re.match(r"^(\d{4})_", f.name)
        if m and f.suffix.lower() in EXT_IMAGEN | EXT_VIDEO:
            grupos.setdefault(m.group(1), []).append(f)
    for k in grupos:
        grupos[k].sort(key=_orden_natural)
    return grupos


def _orden_natural(p: Path):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", p.stem)]


def leer_dia(carpeta: Path) -> list[Publicacion]:
    textos_md = carpeta / "Textos.md"
    if not textos_md.exists():
        return []
    fecha, textos = leer_textos(textos_md)
    if fecha is None:
        return []
    pubs: list[Publicacion] = []

    def nueva(hhmm, red, tipo, medios, portada=None):
        info = textos.get(hhmm, {}).get(red, {})
        cuando = datetime.combine(fecha, time(int(hhmm[:2]), int(hhmm[2:])), ZONA)
        p = Publicacion(
            id=f"{fecha.isoformat()}_{hhmm}_{red}_{tipo}",
            cuando=cuando, red=red, tipo=tipo, medios=medios,
            texto=info.get("texto", ""), titulo=info.get("titulo", ""), portada=portada,
        )
        if tipo != "story" and not p.texto:
            p.avisos.append("sin texto en Textos.md")
        pubs.append(p)

    # Feed: imágenes y carruseles por red
    for nombre, redes in CARPETAS_RED.items():
        for hhmm, medios in _agrupar_por_hora(carpeta / nombre).items():
            tipo = "carrusel" if len(medios) > 1 else "imagen"
            for red in redes:
                nueva(hhmm, red, tipo, medios)

    # Stories: Instagram y Facebook (solo imagen)
    for hhmm, medios in _agrupar_por_hora(carpeta / "4_Stories").items():
        for red in ("instagram", "facebook"):
            nueva(hhmm, red, "story", medios[:1])

    # Reel: a todas las redes
    reel_dir = carpeta / "5_Reel"
    portada = next((f for f in reel_dir.glob("portada*") if f.suffix.lower() in EXT_IMAGEN), None) \
        if reel_dir.is_dir() else None
    for hhmm, medios in _agrupar_por_hora(reel_dir).items():
        videos = [m for m in medios if m.suffix.lower() in EXT_VIDEO]
        if videos:
            for red in ("instagram", "facebook", "tiktok", "linkedin"):
                nueva(hhmm, red, "video", videos[:1], portada)

    pubs.sort(key=lambda p: (p.cuando, p.red))
    return pubs


def construir_calendario(raiz: Path) -> list[Publicacion]:
    todas: list[Publicacion] = []
    for textos in sorted(raiz.glob("*/*/Textos.md")):
        if textos.parent.parent.name.startswith((".", "bot")):
            continue
        todas.extend(leer_dia(textos.parent))
    todas.sort(key=lambda p: (p.cuando, p.red))
    return todas
