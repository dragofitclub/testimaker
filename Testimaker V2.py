# app_testimonios.py
# -*- coding: utf-8 -*-
"""
App de Streamlit para crear testimonios con foto comparativa (antes/después)
Autor: Rodrigo & ChatGPT
"""

from __future__ import annotations
from io import BytesIO
from datetime import datetime

import streamlit as st
from PIL import Image, ImageOps

# =========================
# Configuración básica
# =========================
st.set_page_config(page_title="TestiMaker", page_icon="💬", layout="centered")

# ---------- THEME (paleta EvaluApp) ----------
def inject_theme():
    st.markdown("""
    <style>

      :root {
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
        background: linear-gradient(180deg,var(--rd-bg-start),var(--rd-bg-end)) fixed;
        color: var(--rd-text);
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

      .stButton>button{
        background: var(--rd-accent) !important;
        color: #fff !important;
      }

      [data-testid="stFormSubmitter"] button{
        background-color:#6B8E23 !important;
        color:#FFFFFF !important;
      }

      [data-testid="stDownloadButton"] button{
        background-color:#6B8E23 !important;
        color:#FFFFFF !important;
      }

      [data-testid="stFileUploaderDropzone"]{
        background-color:#EAF6F3 !important;
      }

      [data-testid="stTextInput"] input,
      [data-testid="stTextArea"] textarea,
      [data-testid="stNumberInput"] input{
        background: var(--rd-input-bg) !important;
        border: 1px solid var(--rd-input-border) !important;
        color: var(--rd-text) !important;
      }

      label{
        color: var(--rd-text) !important;
        opacity: 1 !important;
        font-weight: 600 !important;
      }

      /* ===================================================================
         ⭐ FIX DEFINITIVO PARA SAFARI (Streamlit Cloud + radios)
         =================================================================== */

      /* Fuerza color del texto en CUALQUIER nodo dentro del radiogroup */
      div[data-testid="stRadio"] * {
          color: var(--rd-text) !important;
          opacity: 1 !important;
          font-weight: 600 !important;
      }

      /* Fuerza color en spans incluso dentro de Shadow DOM */
      div[data-testid="stRadio"] span {
          color: var(--rd-text) !important;
          opacity: 1 !important;
          font-weight: 600 !important;
      }

      /* Safari coloca el texto en un DIV oculto, lo forzamos también */
      div[role="radiogroup"] div[role="radio"] * {
          color: var(--rd-text) !important;
          opacity: 1 !important;
          font-weight: 600 !important;
      }

      /* A veces Safari encierra el texto en un <p> invisible – también se forza */
      div[data-testid="stRadio"] p {
          color: var(--rd-text) !important;
          opacity: 1 !important;
          font-weight: 600 !important;
      }

    </style>
    """, unsafe_allow_html=True)

inject_theme()

st.title("📖 Bitácora de Resultados")
st.caption("Ingresa tu información, sube tus fotos y genera tu testimonio listo para compartir.")

# =========================
# Utilidades
# =========================
def _abrir_img(file) -> Image.Image:
    img = Image.open(file)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img

def _juntar_lado_a_lado(img_izq: Image.Image, img_der: Image.Image, alto_objetivo: int = 900, separador_px: int = 0) -> Image.Image:
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
    canvas.paste(izq, (0, 0))
    canvas.paste(der, (izq.width + separador_px, 0))
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
    st.markdown("<div class='rd-card'>", unsafe_allow_html=True)

    peso_inicial = st.number_input("1) Peso inicial (kg)", min_value=0.0, step=0.1, format="%.1f")
    peso_actual = st.number_input("2) Peso actual (kg)", min_value=0.0, step=0.1, format="%.1f")

    como_estabas = st.text_area("3) ¿Cómo te encontrabas antes de empezar? (energía, digestión, dolores, etc.)", height=100)
    como_te_sentias = st.text_area("4) ¿Cómo te sentías respecto a tu situación?", height=100)
    por_que_cambio = st.text_area("5) ¿Por qué decidiste que era momento de hacer un cambio?", height=80)
    en_que_ayudo = st.text_area("6) ¿En qué te ayudó el servicio que no podías resolver por tu cuenta?", height=100)
    mejoras_no_peso = st.text_area("7) ¿Qué mejoras no relacionadas con el peso has logrado?", height=100)
    como_te_sientes_hoy = st.text_input("8) ¿Cómo te sientes al respecto (hoy)?")
    objetivo_siguiente = st.text_input("9) ¿Cuál es tu siguiente objetivo?")

    st.write("**¿Cómo te sentirías si compartieras tu resultado con otras personas?**")

    opciones = [
        "Me encantaría 🤩",
        "Normal 🤨",
        "Me costaría un poco 🫣"
    ]

    seleccion = st.radio(
        "",
        opciones,
        horizontal=True
    )

    compartir_encanta = seleccion == "Me encantaría 🤩"
    compartir_normal = seleccion == "Normal 🤨"
    compartir_verguenza = seleccion == "Me costaría un poco 🫣"

    foto_inicial = st.file_uploader("10) Subir **Foto inicial**", type=["jpg", "jpeg", "png"])
    foto_actual = st.file_uploader("11) Subir **Foto actual**", type=["jpg", "jpeg", "png"])

    generar = st.form_submit_button("Generar testimonio", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# Procesamiento
# =========================
if generar:
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

        if compartir_verguenza:
            apertura = "Tengo una confesión que hacer. Y aunque no es cómodo ni fácil de hacer, quiero hacerlo porque quizás pueda ayudarle a alguien que se encuentre en la misma situación. "
        elif compartir_encanta:
            apertura = "No te imaginas lo que tengo que contarte 🤩 "
        else:
            apertura = "Tengo algo que me gustaría compartir. "

        diferencia = peso_inicial - peso_actual
        diferencia_str =
