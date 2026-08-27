import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image


# =====================================================
# TÍTULO
# =====================================================

st.title("Reconocimiento Óptico de Caracteres")

st.write(
    "Toma una fotografía de un texto para reconocer "
    "automáticamente su contenido."
)


# =====================================================
# CÁMARA
# =====================================================

img_file_buffer = st.camera_input("Toma una Foto")


# =====================================================
# BARRA LATERAL
# =====================================================

with st.sidebar:

    st.subheader("Configuración")

    filtro = st.radio(
        "Aplicar Filtro",
        (
            "Con Filtro",
            "Sin Filtro"
        )
    )


# =====================================================
# PROCESAMIENTO
# =====================================================

if img_file_buffer is not None:

    # -------------------------------------------------
    # LEER IMAGEN
    # -------------------------------------------------

    bytes_data = img_file_buffer.getvalue()

    cv2_img = cv2.imdecode(
        np.frombuffer(
            bytes_data,
            np.uint8
        ),
        cv2.IMREAD_COLOR
    )


    # -------------------------------------------------
    # APLICAR FILTRO
    # -------------------------------------------------

    if filtro == "Con Filtro":

        cv2_img = cv2.bitwise_not(
            cv2_img
        )


    # -------------------------------------------------
    # CONVERTIR A RGB
    # -------------------------------------------------

    img_rgb = cv2.cvtColor(
        cv2_img,
        cv2.COLOR_BGR2RGB
    )


    # -------------------------------------------------
    # MOSTRAR IMAGEN
    # -------------------------------------------------

    st.subheader("Imagen capturada")

    st.image(
        img_rgb,
        use_container_width=True
    )


    # -------------------------------------------------
    # RECONOCIMIENTO OCR
    # -------------------------------------------------

    text = pytesseract.image_to_string(
        img_rgb
    )


    # =================================================
    # RESULTADOS
    # =================================================

    st.divider()

    st.header("Resultados")

    if text.strip() != "":

        st.success(
            "Texto detectado correctamente."
        )

        st.text_area(
            "Texto reconocido:",
            text,
            height=200
        )

    else:

        st.warning(
            "No se detectó ningún texto. "
            "Intenta tomar una fotografía más clara."
        )
