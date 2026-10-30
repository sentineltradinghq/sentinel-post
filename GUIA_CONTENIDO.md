# Guía de contenido — Sentinel Trading

Esta guía la sigue Claude en cada tarea programada de publicación.

## Marca
- Nombre: Sentinel Trading · redes: @sentineltradinghq (Instagram, Facebook, TikTok)
- Metricool brandId: 7746945 · zona horaria: America/Bogota
- Colores: fondo #0B0F1A, dorado #F5A623, blanco #F0F2F7, gris #969EAF, verde #2ECC71, rojo #E74C3C
- Imagen: 1080×1350 px (vertical), SIEMPRE en JPG (.jpg); TikTok rechaza PNG, fuente DejaVu Sans, cuadrícula sutil de fondo, "SENTINEL TRADING" arriba en dorado, @sentineltradinghq y "Contenido educativo. No es asesoría financiera." abajo.

## Horarios
- 7:30 a. m. → educativo (se prepara a las 6:02 a. m.): conceptos de trading, cripto, consejos, gestión de riesgo, psicología.
- 7:00 p. m. → Sentinel: avances del proyecto, comunidad, resultados con transparencia, mercado del día.

## Tono
- Cercano y directo (tuteando), pero con contenido profesional y correcto.
- Frases cortas, emojis con moderación, una pregunta al final para generar comentarios.

## Reglas
1. NO revelar cómo funcionan los bots: nada de indicadores exactos, parámetros, RSI, Bandas de Bollinger, multiplicadores ni "la receta". Solo conceptos generales y resultados.
2. Nada de promesas de ganancias ni lenguaje de "inversión/rentabilidad garantizada". Mostrar también pérdidas cuando se hable de resultados.
3. Siempre cerrar el texto con: "🔗 Comunidad gratis y web: en el primer comentario y en nuestra bio." + "Contenido educativo. No es asesoría financiera." + 4-6 hashtags.
4. Primer comentario (firstCommentText) siempre:
   🔗 Únete gratis a la comunidad: https://discord.gg/CXgNyKJRtu
   🌐 Conoce Sentinel: https://sentinel-algo.whop.site
5. Redes: facebook, instagram y tiktok (tiktokData con title corto y privacyOption PUBLIC_TO_EVERYONE).
7. Límite de Instagram: el texto del post debe tener MENOS de 2.000 caracteres (Instagram rechaza más de 2.200 y el post falla). Si el texto es más largo, crear un post aparte solo para Instagram con una versión resumida.
8. Carruseles: hasta 10 imágenes JPG en el mismo post (media con varias URLs). Instagram y TikTok los muestran como carrusel deslizable; Facebook como post con varias fotos.
6. No repetir temas: revisar `temas_publicados.md` antes de elegir y añadir el tema nuevo al final.

## Flujo
1. Elegir tema (sin repetir), redactar texto, generar imagen con Pillow.
2. Guardar la imagen en `posts/AAAA-MM/AAAA-MM-DD_am|pm_tema.jpg`, commit y push a main.
3. Crear borrador en Metricool (draft: true) con media = https://raw.githubusercontent.com/sentineltradinghq/sentinel-post/main/<ruta>
4. Mostrar al usuario la imagen y el texto y esperar "aprobado" o cambios.
5. Con "aprobado": pasar a draft false a la hora del horario (o 5 min después si ya pasó).
6. Historia: con la misma aprobación, crear la historia para Instagram y Facebook:
   `python tools/historia.py posts/.../imagen.jpg historias/AAAA-MM/AAAA-MM-DD_am|pm_historia.jpg "NUEVO POST"`
   (si es carrusel, usar la portada). Commit y push, y programar en Metricool 5 minutos después del post:
   providers instagram + facebook, instagramData {"type":"STORY"}, facebookData {"type":"STORY"}, text vacío, sin primer comentario.
   No usar emojis en el texto de la imagen (la fuente no los muestra).
