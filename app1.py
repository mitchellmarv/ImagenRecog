import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract

from PIL import Image
from gtts import gTTS
from googletrans import Translator
from PyPDF2 import PdfReader


# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Lector Académico",
    page_icon="📚",
    layout="wide"
)


# =====================================================
# VARIABLES
# =====================================================

text = ""

translator = Translator()


# =====================================================
# CARPETA PARA AUDIOS
# =====================================================

if not os.path.exists("temp"):
    os.mkdir("temp")


# =====================================================
# ELIMINAR ARCHIVOS ANTIGUOS
# =====================================================

def remove_files(n):

    mp3_files = glob.glob("temp/*mp3")

    if len(mp3_files) != 0:

        now = time.time()

        n_days = n * 86400

        for f in mp3_files:

            if os.stat(f).st_mtime < now - n_days:

                os.remove(f)

                print("Deleted ", f)


remove_files(7)


# =====================================================
# TEXTO A AUDIO
# =====================================================

def text_to_speech(
    input_language,
    output_language,
    text,
    tld
):

    translation = translator.translate(
        text,
        src=input_language,
        dest=output_language
    )

    trans_text = translation.text

    tts = gTTS(
        trans_text,
        lang=output_language,
        tld=tld,
        slow=False
    )

    # Nombre seguro para evitar problemas
    # con caracteres especiales

    my_file_name = "academic_audio"

    tts.save(
        f"temp/{my_file_name}.mp3"
    )

    return my_file_name, trans_text


# =====================================================
# TÍTULO
# =====================================================

st.title("📚 Lector de Textos Académicos")

st.subheader(
    "Convierte documentos académicos en texto, "
    "traducciones y audio."
)


st.write(
    "Sube un PDF, una imagen o utiliza la cámara "
    "para extraer el contenido de un texto académico."
)


# =====================================================
# SELECCIÓN DE FUENTE
# =====================================================

st.sidebar.header("📂 Fuente del documento")


fuente = st.sidebar.radio(
    "Selecciona cómo quieres ingresar el texto:",
    (
        "📄 PDF",
        "🖼️ Imagen",
        "📷 Cámara"
    )
)


# =====================================================
# VARIABLES
# =====================================================

texto_extraido = ""


# =====================================================
# PDF
# =====================================================

if fuente == "📄 PDF":

    st.header("📄 Subir documento académico")

    pdf_file = st.file_uploader(
        "Selecciona un PDF",
        type=["pdf"]
    )


    if pdf_file is not None:

        st.success(
            "PDF cargado correctamente."
        )


        # ---------------------------------------------
        # LECTURA DEL PDF
        # ---------------------------------------------

        try:

            reader = PdfReader(pdf_file)

            numero_paginas = len(
                reader.pages
            )


            st.info(
                f"El documento contiene "
                f"{numero_paginas} páginas."
            )


            texto_paginas = []


            for pagina in reader.pages:

                contenido = pagina.extract_text()

                if contenido:

                    texto_paginas.append(
                        contenido
                    )


            texto_extraido = "\n\n".join(
                texto_paginas
            )


            if texto_extraido.strip() != "":

                st.success(
                    "Texto extraído correctamente."
                )


            else:

                st.warning(
                    "Este PDF parece estar compuesto "
                    "por imágenes. Para estos documentos "
                    "se recomienda utilizar la opción "
                    "'Imagen' o realizar OCR."
                )


        except Exception as e:

            st.error(
                f"No se pudo leer el PDF: {e}"
            )


# =====================================================
# IMAGEN
# =====================================================

elif fuente == "🖼️ Imagen":

    st.header("🖼️ Subir imagen")

    bg_image = st.file_uploader(
        "Selecciona una imagen",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )


    if bg_image is not None:

        st.image(
            bg_image,
            caption="Imagen cargada",
            use_container_width=True
        )


        # ---------------------------------------------
        # PROCESAR IMAGEN
        # ---------------------------------------------

        image = Image.open(
            bg_image
        )


        img_rgb = np.array(
            image
        )


        texto_extraido = pytesseract.image_to_string(
            img_rgb
        )


        if texto_extraido.strip() != "":

            st.success(
                "Texto detectado correctamente."
            )

        else:

            st.warning(
                "No se detectó texto en la imagen."
            )


# =====================================================
# CÁMARA
# =====================================================

elif fuente == "📷 Cámara":

    st.header("📷 Capturar texto")

    img_file_buffer = st.camera_input(
        "Toma una fotografía del texto"
    )


    # ---------------------------------------------
    # FILTRO
    # ---------------------------------------------

    filtro = st.sidebar.radio(
        "Aplicar filtro a la imagen:",
        (
            "Sí",
            "No"
        )
    )


    if img_file_buffer is not None:

        bytes_data = (
            img_file_buffer.getvalue()
        )


        cv2_img = cv2.imdecode(
            np.frombuffer(
                bytes_data,
                np.uint8
            ),
            cv2.IMREAD_COLOR
        )


        # -----------------------------------------
        # FILTRO
        # -----------------------------------------

        if filtro == "Sí":

            cv2_img = cv2.bitwise_not(
                cv2_img
            )


        # -----------------------------------------
        # RGB
        # -----------------------------------------

        img_rgb = cv2.cvtColor(
            cv2_img,
            cv2.COLOR_BGR2RGB
        )


        # -----------------------------------------
        # MOSTRAR
        # -----------------------------------------

        st.image(
            img_rgb,
            caption="Texto capturado",
            use_container_width=True
        )


        # -----------------------------------------
        # OCR
        # -----------------------------------------

        texto_extraido = pytesseract.image_to_string(
            img_rgb
        )


# =====================================================
# RESULTADOS
# =====================================================

if texto_extraido.strip() != "":

    st.divider()

    st.header("📋 Resultados")

    st.success(
        "Texto extraído correctamente."
    )


    # ---------------------------------------------
    # TEXTO ORIGINAL
    # ---------------------------------------------

    st.subheader(
        "Texto detectado"
    )


    st.text_area(
        "Contenido del documento:",
        texto_extraido,
        height=300
    )


    # =================================================
    # CONFIGURACIÓN DE TRADUCCIÓN
    # =================================================

    st.sidebar.divider()

    st.sidebar.header(
        "🌎 Traducción y audio"
    )


    # ---------------------------------------------
    # IDIOMA DE ENTRADA
    # ---------------------------------------------

    in_lang = st.sidebar.selectbox(

        "Idioma del texto:",

        (
            "Inglés",
            "Español",
            "Bengalí",
            "Coreano",
            "Mandarín",
            "Japonés",
            "Alemán",
            "Ruso"
        )
    )


    idiomas = {

        "Inglés": "en",

        "Español": "es",

        "Bengalí": "bn",

        "Coreano": "ko",

        "Mandarín": "zh-cn",

        "Japonés": "ja",

        "Alemán": "de",

        "Ruso": "ru"
    }


    input_language = idiomas[
        in_lang
    ]


    # ---------------------------------------------
    # IDIOMA DE SALIDA
    # ---------------------------------------------

    out_lang = st.sidebar.selectbox(

        "Idioma de traducción:",

        (
            "Inglés",
            "Español",
            "Bengalí",
            "Coreano",
            "Mandarín",
            "Japonés",
            "Alemán",
            "Ruso"
        )
    )


    output_language = idiomas[
        out_lang
    ]


    # ---------------------------------------------
    # ACENTO
    # ---------------------------------------------

    english_accent = st.sidebar.selectbox(

        "Acento:",

        (
            "Defecto",
            "Reino Unido",
            "Estados Unidos",
            "Canadá",
            "Australia",
            "Irlanda",
            "Sudáfrica"
        )
    )


    if english_accent == "Defecto":

        tld = "com"

    elif english_accent == "Reino Unido":

        tld = "co.uk"

    elif english_accent == "Estados Unidos":

        tld = "com"

    elif english_accent == "Canadá":

        tld = "ca"

    elif english_accent == "Australia":

        tld = "com.au"

    elif english_accent == "Irlanda":

        tld = "ie"

    elif english_accent == "Sudáfrica":

        tld = "co.za"


    # =================================================
    # OPCIONES
    # =================================================

    st.sidebar.divider()

    mostrar_traduccion = st.sidebar.checkbox(
        "Mostrar traducción"
    )


    convertir_audio = st.sidebar.checkbox(
        "Convertir traducción a audio"
    )


    # =================================================
    # BOTÓN
    # =================================================

    if st.sidebar.button(
        "🔊 Procesar texto"
    ):

        try:

            # -----------------------------------------
            # TRADUCCIÓN
            # -----------------------------------------

            result_audio, output_text = (
                text_to_speech(
                    input_language,
                    output_language,
                    texto_extraido,
                    tld
                )
            )


            # -----------------------------------------
            # MOSTRAR TRADUCCIÓN
            # -----------------------------------------

            if mostrar_traduccion:

                st.subheader(
                    "🌎 Texto traducido"
                )

                st.text_area(
                    "Traducción:",
                    output_text,
                    height=300
                )


            # -----------------------------------------
            # AUDIO
            # -----------------------------------------

            if convertir_audio:

                audio_file = open(
                    f"temp/{result_audio}.mp3",
                    "rb"
                )


                audio_bytes = (
                    audio_file.read()
                )


                st.subheader(
                    "🔊 Audio del texto"
                )


                st.audio(
                    audio_bytes,
                    format="audio/mp3"
                )


        except Exception as e:

            st.error(
                "Ocurrió un error durante "
                f"el procesamiento: {e}"
            )


# =====================================================
# MENSAJE INICIAL
# =====================================================

else:

    st.info(
        "📚 Selecciona una fuente y carga un "
        "documento para comenzar."
    )
