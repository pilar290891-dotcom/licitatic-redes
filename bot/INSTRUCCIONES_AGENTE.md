# Texto para las instrucciones del proyecto de Claude (agente de contenido)

Copia este bloque en las instrucciones de tu proyecto de Claude para que el agente entregue
siempre el formato que el bot sabe publicar.

---

**Formato de entrega para el bot de publicación (obligatorio)**

Cada semana sube el contenido al repositorio `licitatic-redes` en `semana-DD-DD/` con una carpeta
por día llamada `N_Dia_DD` (por ejemplo `2_Miercoles_11`). Dentro de cada día:

- `1_Instagram_y_Facebook/`, `2_TikTok/`, `3_LinkedIn/`: imágenes que empiezan por la hora en formato
  HHMM y un guion bajo (`1630_carrusel_1.jpg`, `1330_en_serio.jpg`). Varias imágenes con la misma hora
  forman un carrusel, en orden por el número final.
- `4_Stories/`: stories de Instagram y Facebook con el mismo prefijo de hora (`1800_storie.jpg`).
- `5_Reel/`: el vídeo vertical `HHMM_reel.mp4` y su portada `portada_reel.jpg`.
- `Textos.md` con:
  - Primera línea: `# <Día> DD/MM · Textos`.
  - Una sección por publicación que empiece por `## HH:MM · <nombre>`, con la misma hora que los archivos.
  - Dentro, un bloque por red que empiece con su nombre en negrita: `**Instagram / Facebook**`,
    `**IG / FB / TikTok (título: …)**`, `**TikTok** (título: …)`, `**LinkedIn** (documento: …)`.
    Todo lo que va debajo, hasta el siguiente bloque, es el copy que se publica tal cual, hashtags incluidos.
  - En LinkedIn, «documento: título» hace que el carrusel se publique como documento PDF deslizable.
- No uses otras horas en los nombres de archivo que no tengan su sección en `Textos.md`
  (salvo las stories, que no llevan texto).
- Sube cada semana como muy tarde el día antes de la primera publicación.
