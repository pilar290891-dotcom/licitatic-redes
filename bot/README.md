# Bot de publicación de LicitaTIC

Publica solo, cada día y a su hora, lo que el agente de contenido deja en este repositorio.
Es gratis: corre en GitHub Actions y usa las APIs oficiales de cada red.

## Cómo funciona

1. El agente de contenido (proyecto de Claude) sube cada semana una carpeta `semana-XX-YY/`
   con un subcarpeta por día (`2_Miercoles_11/`, …) que contiene `Textos.md` y las imágenes y el reel.
2. Cada 15 minutos, GitHub Actions ejecuta `python -m bot.main publicar`.
3. El bot lee el horario de cada `Textos.md`, mira qué toca a esa hora y lo publica en cada red con su copy.
4. Lo publicado se anota en `bot/estado/publicados.json`, así nada sale dos veces.

| Carpeta del día           | Se publica en                              | Hora                     |
|---------------------------|--------------------------------------------|--------------------------|
| `1_Instagram_y_Facebook/` | Instagram y Facebook (imagen o carrusel)   | la del nombre: `1630_…` = 16:30 |
| `2_TikTok/`               | TikTok (fotos)                             | ídem                     |
| `3_LinkedIn/`             | LinkedIn (imagen, o documento PDF si el Textos.md dice «documento: …») | ídem |
| `4_Stories/`              | Stories de Instagram y Facebook            | ídem                     |
| `5_Reel/`                 | Reel en Instagram, Facebook, TikTok y LinkedIn (`portada_reel.jpg` como portada) | ídem |

Solo publica lo que tocaba en las últimas 3 horas (`VENTANA_HORAS`), para que al encenderlo
no se publique de golpe contenido atrasado.

## Interruptor general

Mientras no exista la variable `PUBLICAR = si`, el bot **solo simula** y muestra en el resumen
de cada ejecución lo que habría publicado.

En GitHub: **Settings → Secrets and variables → Actions → pestaña Variables → New repository variable**.

| Variable             | Valor                                                            |
|----------------------|------------------------------------------------------------------|
| `PUBLICAR`           | `si` para publicar de verdad                                     |
| `REDES`              | opcional, p. ej. `instagram,facebook` para limitar redes          |
| `TIKTOK_PRIVACIDAD`  | `PUBLIC_TO_EVERYONE` cuando TikTok apruebe la app                 |
| `BASE_URL_MEDIOS`    | opcional, dominio propio verificado para las fotos de TikTok     |

Las claves de cada red van en la pestaña **Secrets** del mismo sitio. Una red sin sus secretos
simplemente se salta.

## Conectar cada red (una sola vez)

### Instagram y Facebook (Meta)
Requisitos: Instagram en modo **cuenta profesional** y vinculado a la página de Facebook de LicitaTIC.

1. Entra en <https://developers.facebook.com> → **Crear app** → tipo «Empresa».
2. Añade los productos **Instagram Graph API** y **Facebook Login for Business**.
3. En **Herramientas → Explorador de la API Graph**, elige tu app y pide estos permisos:
   `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`,
   `instagram_content_publish`, `instagram_manage_insights`, `business_management`.
4. Genera el token, cámbialo por uno de larga duración en el **Depurador de tokens** («Extender token»),
   y con él llama a `me/accounts`: el `access_token` de tu página es el `META_TOKEN` (no caduca)
   y el `id` es el `META_PAGE_ID`.
5. Llama a `{META_PAGE_ID}?fields=instagram_business_account`: ese id es el `META_IG_USER_ID`.

Como solo publicas en tus propias cuentas, no hace falta pasar la revisión de Meta.

### LinkedIn
1. Entra en <https://www.linkedin.com/developers/apps> → **Create app**, asociada a la página de LicitaTIC.
2. En **Products**, añade «Share on LinkedIn» (perfil personal) y solicita
   «Community Management API» si quieres publicar como página de empresa (LinkedIn la revisa).
3. En **Auth → OAuth 2.0 tools** genera un token con `w_member_social`
   (o `w_organization_social` para la página). Es el `LINKEDIN_TOKEN`; dura 60 días y hay que renovarlo.
4. `LINKEDIN_AUTHOR` es `urn:li:organization:<número de tu página>` o `urn:li:person:<tu id>`.

### TikTok
1. Entra en <https://developers.tiktok.com> → **Manage apps** → crea una app.
2. Añade los productos **Login Kit** y **Content Posting API** con «Direct Post» activado,
   y el permiso `video.publish`.
3. Autoriza la app con tu cuenta y guarda el `refresh_token` (dura un año):
   `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` y `TIKTOK_REFRESH_TOKEN`.
4. Pide la **auditoría** de la app. Hasta que la aprueben, TikTok solo deja publicar en privado.
5. Las fotos/carruseles exigen un dominio verificado en la app (por ejemplo `licitatic.es`) y
   `BASE_URL_MEDIOS` apuntando a él. Los reels funcionan sin eso.

## Probar en local

```bash
pip install -r bot/requirements.txt
python -m bot.main listar --dias 7     # calendario de la semana
python -m bot.main publicar            # simulación (sin PUBLICAR=si)
```

## Limitaciones conocidas
- Las encuestas de las stories (A/B/C) no se pueden añadir por API: se publica la imagen.
- GitHub puede retrasar unos minutos las ejecuciones programadas.
- El repositorio debe seguir siendo público para que Meta descargue las imágenes.
