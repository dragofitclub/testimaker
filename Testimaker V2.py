# app_testimonios.py
# -*- coding: utf-8 -*-
"""
App de Streamlit para crear testimonios con foto comparativa (antes/después)
Autor: Rodrigo & ChatGPT
"""

from __future__ import annotations
from io import BytesIO
from pathlib import Path
import base64

import streamlit as st
from PIL import Image, ImageOps

# =========================
# Configuración de página
# =========================
st.set_page_config(page_title="TestiMaker", page_icon="💬", layout="centered")

# =========================
# CSS: modo claro forzado incluso en Safari
# =========================
def inject_theme():
    st.markdown("""
    <style>

      /* 🔥 Fuerza modo claro incluso en Safari/macOS */
      html, body, [data-testid="stAppViewContainer"], * {
        color-scheme: light !important;
      }

      :root{
        --rd-bg-start:#FFF9F4;
        --rd-bg-end:#F7F3EE;
        --rd-card:#FFFFFF;
        --rd-border:#EAE6E1;
        --rd-accent:#3A6B64;
        --rd-accent-2:#8BBFB5;
        --rd-text:#1F2A2E;
        --rd-pill-bg:#EAF6F3;
        --rd-shadow:0 10px 24px rgba(20,40,40,.08);
        --rd-radius:18px;
        --rd-input-bg:#EEF4F2;
        --rd-input-border:#D5E2DE;
      }

      [data-testid="stAppViewContainer"]{
        background: linear-gradient(180deg,var(--rd-bg-start),var(--rd-bg-end)) fixed !important;
        color: var(--rd-text) !important;
      }

      .block-container{ max-width: 980px; }

      h1, h2, h3{
        color: var(--rd-accent);
      }

      .rd-card{
        background: var(--rd-card);
        border: 1px solid var(--rd-border);
        border-radius: var(--rd-radius);
        box-shadow: var(--rd-shadow);
        padding: 16px 18px;
      }

      /* Inputs & labels */
      input, textarea, select {
        background-color: var(--rd-input-bg) !important;
        border: 1px solid var(--rd-input-border) !important;
        color: var(--rd-text) !important;
      }

      label, .st-ae {
        color: var(--rd-text) !important;
        opacity: 1 !important;
        font-weight: 600 !important;
      }

      div[data-testid="stRadio"] * {
        color: var(--rd-text) !important;
        fill: var(--rd-text) !important;
        stroke: var(--rd-text) !important;
        opacity: 1 !important;
      }

      /* Botón */
      button[data-testid="stBaseButton-secondaryFormSubmit"] {
          background-color: #8CAC3F !important;
          color: white !important;
          border-radius: 40px !important;
          padding: 14px 20px !important;
          font-size: 17px !important;
          font-weight: 600 !important;
          border: none !important;
          width: 100% !important;
      }

      /* Uploader */
      [data-testid="stFileUploader"] button {
          background-color: #8CAC3F !important;
          color: white !important;
          border-radius: 25px !important;
          padding: 8px 20px !important;
          font-size: 14px !important;
          font-weight: 600 !important;
          border: none !important;
      }

      [data-testid="stFileUploaderDropzone"] {
          background-color: #EAF6F3 !important;
          border: 1px solid #8BBFB5 !important;
          border-radius: 18px !important;
          padding: 12px !important;
      }

      [data-testid="stFileUploaderDropzone"] * {
          color: #3A6B64 !important;
          font-weight: 600 !important;
      }

      /* Logo fijo */
      .logo-fixed {
          position: fixed;
          top: 50px;
          right: 25px;
          width: 120px;
          z-index: 9999;
          opacity: 1;
      }

    </style>
    """, unsafe_allow_html=True)

inject_theme()


# =========================
# Logo
# =========================
APP_DIR = Path(__file__).parent.resolve()
logo_path = APP_DIR / "logo.png"

if logo_path.exists():
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<img src="data:image/png;base64,{logo_b64}" class="logo-fixed">',
        unsafe_allow_html=True
    )


# =========================
# Funciones de imagen
# =========================
def _abrir_img(file) -> Image.Image:
    img = Image.open(file)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def _juntar_lado_a_lado(img_izq: Image.Image, img_der: Image.Image, alto_objetivo=900):
    izq = img_izq.resize((int(img_izq.width * (alto_objetivo / img_izq.height)), alto_objetivo))
    der = img_der.resize((int(img_der.width * (alto_objetivo / img_der.height)), alto_objetivo))
    canvas = Image.new("RGB", (izq.width + der.width, alto_objetivo), (255, 255, 255))
    canvas.paste(izq, (0, 0))
    canvas.paste(der, (izq.width, 0))
    return canvas


def _png_bytes(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


# =========================
# UI
# =========================
st.title("📖 Bitácora de Resultados")
st.caption("Ingresa tu información, sube tus fotos y genera tu testimonio listo para compartir.")

with st.form("form_testimonio"):
    st.markdown("<div class='rd-card'>", unsafe_allow_html=True)

    peso_inicial = st.number_input("1) Peso inicial (kg)", min_value=0.0, step=0.1)
    peso_actual = st.number_input("2) Peso actual (kg)", min_value=0.0, step=0.1)

    como_estabas = st.text_area("3) ¿Cómo te encontrabas antes de empezar?", height=100)
    como_te_sentias = st.text_area("4) ¿Cómo te sentías respecto a tu situación?", height=100)
    por_que_cambio = st.text_area("5) ¿Por qué decidiste hacer un cambio?", height=80)
    en_que_ayudo = st.text_area("6) ¿En qué te ayudó el servicio?", height=100)
    mejoras_no_peso = st.text_area("7) ¿Qué mejoras no relacionadas con el peso has logrado?", height=100)
    como_te_sientes_hoy = st.text_input("8) ¿Cómo te sientes hoy?")
    objetivo_siguiente = st.text_input("9) ¿Cuál es tu siguiente objetivo?")

    st.write("**¿Cómo te sentirías si compartieras tu resultado?**")

    seleccion = st.radio("", ["Me encantaría 🤩", "Normal 🤨", "Me costaría un poco 🫣"], horizontal=True)

    foto_inicial = st.file_uploader("10) Subir **Foto inicial**", type=["jpg","jpeg","png"])
    foto_actual = st.file_uploader("11) Subir **Foto actual**", type=["jpg","jpeg","png"])

    generar = st.form_submit_button("Generar testimonio", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


if generar:
    img_antes = _abrir_img(foto_inicial)
    img_despues = _abrir_img(foto_actual)
    imagen_final = _juntar_lado_a_lado(img_antes, img_despues)

    st.image(imagen_final, use_container_width=True)

    st.download_button(
        label="⬇️ Descargar imagen (PNG)",
        data=_png_bytes(imagen_final),
        file_name="testimonio.png",
        mime="image/png",
        use_container_width=True
    )
