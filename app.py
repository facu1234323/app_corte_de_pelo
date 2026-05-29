import streamlit as st
import replicate
import os
import requests
from io import BytesIO
from PIL import Image

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="BarberAI Visual", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    /* Estilo general oscuro */
    .main { background-color: #0e1117; }
    
    /* Efecto "Tarjeta" para que la imagen y el botón parezcan uno solo */
    .stButton > button {
        width: 100%;
        border-radius: 0px 0px 8px 8px; /* Bordes redondeados solo abajo */
        border: 2px solid #5d3fd3;
        border-top: none; /* Quitamos el borde superior para pegarlo a la foto */
        background-color: #1a1a1a;
        color: white;
        font-weight: bold;
        margin-top: -15px; /* Sube el botón para fusionarse con la foto */
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #5d3fd3;
        color: white;
    }
    
    /* Efecto estético a las imágenes de los cortes */
    [data-testid="stImage"] > img {
        border-radius: 8px 8px 0px 0px; /* Bordes redondeados solo arriba */
        border: 2px solid #5d3fd3;
        border-bottom: none;
    }
    
    [data-testid="column"] {
        text-align: center;
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE LA IA ---
os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def mandar_prompt(imagen_bytes, instruccion_final):
    try:
        prompt_final = (
                f"A professional studio portrait of the SAME PERSON as in the input image.

                Keep their facial features, identity, and expression exactly the same.

                Only change the hairstyle to: {instruccion_final}

                Highly detailed hair texture, 4k resolution.

                A hyperrealistic studio portrait of the same person as in the input image.

                Keep their facial features, identity, expression, and neck structure exactly the same.

                Do not change the person's face. Only modify the hair.

                I forbid you from modifying any details of the face, only the hair; the entire face must remain the same.

                Maintain the same photo structure, facial position, feature structure, and expression.

                Cinematic studio lighting.

                I want you to change the hair exactly as the prompt asks and replicate it exactly as instructed.
        ")
        output = replicate.run(
            "google/nano-banana-2",
            input={
                "prompt": prompt_final,
                "image_input": [BytesIO(imagen_bytes)],
                "resolution": "1K",
                "aspect_ratio": "1:1",
                "output_format": "jpg"
            }
        )
        res = output[0] if isinstance(output, list) else output
        return res.url if hasattr(res, 'url') else str(res)
    except Exception as e:
        return f"Error: {str(e)}"

# --- LISTA DE LOS 35 CORTES ---
# Armé esta lista basándome en los textos de tu imagen para que cada número tenga su nombre real.
nombres_35_cortes = [
    "Corte de Barba", "Cabello Largo", "Desvanecido", "Cresta Alta", "Pelo Corto Desordenado", "Mechones Largos", "Corte de Cepillo", 
    "Peinado Hacia Lado", "Atrás Desvanecido", "Recogido Atrás", "Cabello Rizado Liso", "Militar Corto", "Hacia Arriba", "Arriba Textura", 
    "Mechones Largos 2", "Rizado Liso 2", "Afro Largo", "Militar Corto 2", "Largo de Capas", "Desvanecido Bajo", "Casual Texturizado", 
    "Undercut Peinado", "Corte de Barba 2", "Corte de Bargo", "Desvanecido Bajo 2", "Desvanecido Bajo 3", "Casual Texturizado 2", 
    "Clásico Hacia Lado", "Barba Completa", "Undercut Peinado 2", "Estilo 31", "Estilo 32", "Estilo 33", "Estilo 34", "Estilo 35"
]

# --- INTERFAZ ---
st.title("✂️ CATÁLOGO INTERACTIVO BARBERÍA")

col_menu, col_visor = st.columns([2, 1], gap="large")

with col_menu:
    archivo = st.file_uploader("📸 1. Subí la foto del cliente", type=["jpg", "png", "jpeg"])
    
    if archivo:
        color_sel = st.selectbox("🎨 2. Elegí el color de pelo:", ["Natural", "Rubio Platino", "Castaño", "Negro Intenso", "Gris Ceniza"])
        st.write("### ✂️ 3. Tocá el estilo que buscás:")
        
        # Armamos una cuadrícula de 5 columnas para que entren bien los 35 cortes
        grid = st.columns(5)
        
        # Bucle mágico: recorre del 1 al 35
        for i in range(1, 36):
            col_actual = grid[(i - 1) % 5]
            with col_actual:
                ruta_imagen = f"cortes/{i}.jpg"
                
                # Intentamos cargar la imagen desde tu carpeta
                try:
                    img_recorte = Image.open(ruta_imagen)
                    st.image(img_recorte, use_container_width=True)
                except FileNotFoundError:
                    st.image("https://via.placeholder.com/150x150/1a1a1a/ffffff/?text=Falta+Imagen", use_container_width=True)
                
                # Obtenemos el nombre correspondiente a ese número (o ponemos Estilo Genérico)
                nombre_corte = nombres_35_cortes[i - 1] if i <= len(nombres_35_cortes) else f"Estilo {i}"
                
                # El botón abajo de la imagen
                if st.button(nombre_corte, key=f"btn_{i}"):
                    with st.spinner("Esculpiendo nuevo look..."):
                        instruccion = f"{nombre_corte} hair style, {color_sel} hair color"
                        st.session_state.resultado = mandar_prompt(archivo.getvalue(), instruccion)

with col_visor:
    st.subheader("✨ Vista Previa")
    if 'resultado' in st.session_state:
        st.image(st.session_state.resultado, use_container_width=True)
        img_data = requests.get(st.session_state.resultado).content
        st.download_button("💾 Guardar Nuevo Look", img_data, "nuevo_corte.png", "image/png")
    else:
        st.info("Subí una foto y elegí un corte del catálogo para ver el resultado.")
