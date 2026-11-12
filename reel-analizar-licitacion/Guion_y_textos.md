# Reel «No leas el pliego entero… todavía»

Vídeo: `Reel_analizar_licitacion_LicitaTIC.mp4` (1080×1920, 9:16, 54 s, 30 fps, con música). Portada: `Portada_reel_analizar_licitacion.jpg`.

Base visual: la imagen del portátil que facilitó Pilar. Dentro de la pantalla aparecen las páginas **reales** de los dos pliegos que facilitó Pilar (REGTSA, expediente 2026/821-PC, suministro de 50 licencias Office 365 E3 EEE sin Teams): el administrativo (PCAP, 17 páginas) y el técnico (PPT, 5 páginas). El subrayado amarillo está colocado sobre el texto exacto de cada pliego. La firma del PPT (nombre y DNI parcial) se ha tapado.

Música: `musica_reel_original.wav`, compuesta por código para este reel (120 BPM, sin muestras ni derechos de terceros), con efectos sincronizados (pasar páginas, rotulador, aparición de tarjetas y sello).

Por petición de Pilar no se usa «GO / NO-GO»: se dice «Presentamos / No presentamos».

## Guion

| Tiempo | Pliego y apartado | Tarjeta (pregunta + dato real) |
|---|---|---|
| 0–6 s | PCAP pasando páginas (1 → 17) | **NO LEAS EL PLIEGO ENTERO** · *…todavía.* · Para decidir si te presentas: subraya primero estas 8 cosas · Pliego real: suministro de 50 licencias Office 365 |
| 6–10 s | PCAP, cl. 2 | 1 · Objeto y CPV · ¿Es exactamente lo que vendes? · 50 licencias Office 365 · canal CSP · CPV 48000000-8 |
| 10–14 s | PCAP, cl. 6 y 7 | 2 · Presupuesto y duración · ¿Te salen los números? · 22.620 € sin IVA · 24 meses · 226,20 € por licencia y año |
| 14–18 s | PCAP, cl. 11 | 3 · Criterios de adjudicación · ¿Puedes competir solo en precio? · Precio: 100 % de la puntuación |
| 18–22 s | PCAP, cl. 12 | 4 · Requisitos para licitar · ¿Cumples lo que piden para presentarte? · Partner CSP de Microsoft + ROLECE · sin solvencia |
| 22–26 s | PCAP, cl. 13 | 5 · Plazo de presentación · ¿Te da tiempo a prepararla bien? · 10 días hábiles · hasta las 14:00 del último día |
| 26–28 s | Cambio de pestaña | Ahora, el pliego técnico |
| 28–32 s | PPT, ap. 2 | 6 · Requisitos técnicos mínimos · Si no lo cumples, quedas fuera. · Ser partner CSP de Microsoft (si no, exclusión) |
| 32–36 s | PPT, ap. 4 y 5 | 7 · Plazos de ejecución · ¿Llegas a tiempo sin cortar el servicio? · Licencias activas el 10 de diciembre de 2026 |
| 36–40 s | PPT, ap. 6 | 8 · Soporte y tiempos · ¿Puedes cumplir estos tiempos? · Acuse en 2 h · actuación en 4 h laborables |
| 40–47 s | Checklist y sello **PRESENTAMOS** | ¿Nos presentamos? ¿Has subrayado las 8? · ¿Encaja todo? Presentamos. · *¿Falla algo clave? No presentamos, y a por la siguiente.* |
| 47–54 s | Cierre de marca | ¿Te ayudamos? · Analizamos el pliego contigo · Y te recomendamos si presentarte o no antes de preparar la oferta. · *Tú decides a cuáles presentarte.* · Guárdalo para tu próximo pliego · www.licitatic.es |

Cada tarjeta se queda unos 3,4 s en pantalla.

## Texto para Instagram
No leas el pliego entero… todavía 👀
Con un pliego real delante, subraya primero estas 8 cosas:
📄 Pliego administrativo: objeto y CPV, presupuesto y duración, criterios de adjudicación, requisitos para licitar y plazo.
🛠️ Pliego técnico: requisitos mínimos, plazos de ejecución y tiempos de soporte.
¿Encaja todo? Presentamos. ¿Falla algo clave? No presentamos, y a por la siguiente.
Guárdalo para tu próximo pliego 📌 ¿Quieres que lo analicemos contigo? 👉 licitatic.es
#licitaciones #licitacionespublicas #contratacionpublica #empresasTIC #pymes #pliegos #licitaTIC

## Texto para TikTok
No leas el pliego entero… todavía 👀 Subraya estas 8 cosas y decide si te presentas o no. Guárdalo 📌
#licitaciones #contratacionpublica #empresastic #pymes #pliegos

## LinkedIn
Leerse un pliego entero para descubrir en la página 15 que no cumples un requisito es tiempo perdido.
Con un pliego real (suministro de 50 licencias Office 365), esto es lo primero que subrayamos:
✅ Objeto y CPV
✅ Presupuesto y duración
✅ Criterios de adjudicación
✅ Requisitos para licitar (aquí: partner CSP y ROLECE)
✅ Plazo de presentación
✅ Requisitos técnicos mínimos
✅ Plazos de ejecución
✅ Soporte y tiempos de respuesta
Si todo encaja, nos presentamos. Si falla algo clave, no nos presentamos, y a por la siguiente.
En LicitaTIC analizamos los pliegos contigo y te recomendamos si presentarte o no. Tú decides a cuáles presentarte. 👉 licitatic.es
#LicitacionesPúblicas #ContrataciónPública #SectorTIC #Pymes

## Cómo regenerarlo
En `_motor/`: `npm i @fontsource/montserrat @fontsource/instrument-serif`, `python3 music.py` y `node build.js` (necesita Playwright y ffmpeg). Las páginas de los pliegos están en `_motor/pdf/` y `pdf/find.py` calcula dónde va cada subrayado.
