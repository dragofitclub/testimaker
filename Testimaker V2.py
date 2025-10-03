# app_testimonios.py
# -*- coding: utf-8 -*-
"""
App de Streamlit para crear testimonios con foto comparativa (antes/después)
Autor: Rodrigo & ChatGPT
Instrucciones:
1) Instala dependencias:  pip install streamlit pillow
2) Ejecuta:               streamlit run app_testimonios.py
"""

from __future__ import annotations
from io import BytesIO
from datetime import datetime

import streamlit as st
from PIL import Image, ImageOps

# =========================
# Configuración básica
# =========================
st.set_page_config(page_title="Creador de Testimonios", page_icon="💬", layout="centered")
st.title("💬 Creador de Testimonios – Bienestar & Puesta en Forma")
st.caption("Ingresa tu información, sube tus fotos y genera tu testimonio listo para compartir.")

# =========================
# Utilidades
# =========================
def _abrir_img(file) -> Image.Image:
    """Abre una imagen de Streamlit FileUploader con corrección de orientación y en RGB."""
    img = Image.open(file)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img

def _juntar_lado_a_lado(img_izq: Image.Image, img_der: Image.Image, alto_objetivo: int = 900, separador_px: int = 0) -> Image.Image:
    """
    Une dos imágenes lado a lado ajustando su alto a 'alto_objetivo' y manteniendo proporciones.
    separador_px: espacio opcional entre imágenes (0 = sin separación).
    """
    # Redimensionar manteniendo proporciones por alto
    def redimensionar(img: Image.Image, alto_target: int) -> Image.Image:
        w, h = img.size
        if h == alto_target:
            return img
        nuevo_w = int(round(w * (alto_target / h)))
        return img.resize((nuevo_w, alto_target), Image.LANCZOS)

    izq = redimensionar(img_izq, alto_objetivo)
    der = redimensionar(img_der, alto_objetivo)

    w_total = izq.width + separador_px + der.width
    canvas = Image.new("RGB", (w_total, alto_objetivo), (255, 255, 255))
    x = 0
    canvas.paste(izq, (x, 0))
    x += izq.width + separador_px
    canvas.paste(der, (x, 0))
    return canvas

def _png_bytes(img: Image.Image) -> bytes:
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.read()

def _formatea_num(n) -> str:
    try:
        return f"{float(n):.1f}".rstrip("0").rstrip(".")
    except Exception:
        return str(n)

# =========================
# Formulario
# =========================
with st.form("form_testimonio"):
    col1, col2 = st.columns(2)
    with col1:
        peso_inicial = st.number_input("1) Peso inicial (kg)", min_value=0.0, step=0.1, format="%.1f")
        como_estabas = st.text_area("3) ¿Cómo te encontrabas antes de empezar? (energía, digestión, dolores, etc.)", height=100)
        por_que_cambio = st.text_area("5) ¿Por qué decidiste que era momento de hacer un cambio?", height=80)
        mejoras_no_peso = st.text_area("7) ¿Qué mejoras no relacionadas con el peso has logrado?", height=100)
        objetivo_siguiente = st.text_input("9) ¿Cuál es tu siguiente objetivo?")
        foto_inicial = st.file_uploader("10) Subir **Foto inicial**", type=["jpg", "jpeg", "png"])
    with col2:
        peso_actual = st.number_input("2) Peso actual (kg)", min_value=0.0, step=0.1, format="%.1f")
        como_te_sentias = st.text_area("4) ¿Cómo te sentías respecto a tu situación?", height=100)
        en_que_ayudo = st.text_area("6) ¿En qué te ayudó el servicio que no podías resolver por tu cuenta?", height=100)
        como_te_sientes_hoy = st.text_input("8) ¿Cómo te sientes al respecto (hoy)?")
        foto_actual = st.file_uploader("11) Subir **Foto actual**", type=["jpg", "jpeg", "png"])

    generar = st.form_submit_button("Generar testimonio")

# =========================
# Procesamiento
# =========================
if generar:
    # Validaciones mínimas
    faltantes = []
    if peso_inicial == 0.0: faltantes.append("Peso inicial")
    if peso_actual == 0.0: faltantes.append("Peso actual")
    if not como_estabas.strip(): faltantes.append("Cómo te encontrabas antes de empezar")
    if not como_te_sentias.strip(): faltantes.append("Cómo te sentías respecto a tu situación")
    if not por_que_cambio.strip(): faltantes.append("Por qué decidiste cambiar")
    if not en_que_ayudo.strip(): faltantes.append("En qué te ayudó el servicio")
    if not mejoras_no_peso.strip(): faltantes.append("Mejoras no relacionadas con el peso")
    if not como_te_sientes_hoy.strip(): faltantes.append("Cómo te sientes al respecto (hoy)")
    if not objetivo_siguiente.strip(): faltantes.append("Siguiente objetivo")
    if not foto_inicial: faltantes.append("Foto inicial")
    if not foto_actual: faltantes.append("Foto actual")

    if faltantes:
        st.error("Por favor completa/sube lo siguiente: " + ", ".join(faltantes))
    else:
        # Calcular diferencia de peso (Respuesta 1 - Respuesta 2)
        diferencia = peso_inicial - peso_actual
        diferencia_str = _formatea_num(diferencia)

        # Construir el texto final
        texto = (
            "Tengo una confesión que hacer. Y aunque no es cómodo ni fácil de hacer, quiero hacerlo porque "
            "quizás pueda ayudarle a alguien que se encuentre en la misma situación. "
            f"Hace no mucho me encontraba {como_estabas.strip()} lo cual me hacía sentir {como_te_sentias.strip()}. "
            f"Decidí que ya no quería seguir así porque {por_que_cambio.strip()} así que busqué ayuda y asesoría. "
            f"Encontré una Tribu que promovia habitos saludables y en ella encontre {en_que_ayudo.strip()} que siempre fue mi mayor reto. "
            f"A la fecha he logrado {mejoras_no_peso.strip()} además de controlar {diferencia_str} kg. "
            f"Me siento {como_te_sientes_hoy.strip()} por lo que he logrado y tengo claro que esto recién es el inicio. "
            f"Mi próximo objetivo es {objetivo_siguiente.strip()}, lo mejor aun esta por venir :)"
        )

        # Crear la imagen lado a lado (Foto 10 y Foto 11)
        try:
            img_antes = _abrir_img(foto_inicial)
            img_despues = _abrir_img(foto_actual)
            imagen_unida = _juntar_lado_a_lado(img_antes, img_despues, alto_objetivo=900, separador_px=0)
        except Exception as e:
            st.error(f"Ocurrió un problema al procesar las imágenes: {e}")
            st.stop()

        # Mostrar previsualización
        st.subheader("✅ Resultado")
        # Cambio aquí: use_container_width en vez de use_column_width
        st.image(imagen_unida, caption="Foto 10 (Inicial) | Foto 11 (Actual) – Imagen combinada", use_container_width=True)

        # Botón de descarga de la imagen
        nombre_archivo = f"testimonio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        st.download_button(
            label="⬇️ Descargar imagen combinada (PNG)",
            data=_png_bytes(imagen_unida),
            file_name=nombre_archivo,
            mime="image/png",
        )

        # Texto listo para copiar y pegar
        st.write("### 📋 Texto listo para copiar y pegar")
        st.text_area("Selecciona y copia el texto:", value=texto, height=220)

        # Resumen útil (opcional)
        with st.expander("Resumen numérico"):
            st.markdown(
                f"- **Peso inicial:** {_formatea_num(peso_inicial)} kg  \n"
                f"- **Peso actual:** {_formatea_num(peso_actual)} kg  \n"
                f"- **Diferencia controlada:** {diferencia_str} kg"
            )
