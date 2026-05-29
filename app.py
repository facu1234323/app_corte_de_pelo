import streamlit as st
import replicate
import os
import requests
from io import BytesIO
from PIL import Image

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="BarberAI Visual", layout="wide")
descripciones = {"Corte de Barba":'I want the haircut to have a sleek, straight-back hairstyle on top, and a very masculine beard. I want it to be thick but not long; it should cover from below the nose down to the chin.',
                 "Cabello Largo":'This cut should be a hippie style, long enough to reach the shoulders, but without losing its masculine character. It should be wavy, but not exaggerated, and slightly messy, but not too much.',
                 "Desvanecido":"A modern, slicked-back haircut with the sides shaved but faded. No bangs, elegant yet with a modern touch. The fade should be medium and noticeable, as that's the essence of the cut.",
                 "Cresta Alta":"",
                 }
catálogo_cortes = {
    # --- FILA 1 ---
    "Corte de Barba": "Hombre con una barba larga, densa y bien perfilada, combinada con un corte de cabello corto y peinado de forma pulcra.",
    "Cabello Largo": "Cabello largo que llega hasta los hombros, con ondas naturales muy suaves y raya en medio.",
    "Desvanecido": "Vista de perfil de un corte con degradado alto (fade) en los laterales y el cabello superior más largo, peinado hacia arriba.",
    "Cresta Alta": "Corte de estilo 'faux hawk' con laterales muy cortos y una cresta pronunciada y estilizada hacia el centro y arriba.",
    "Pelo Corto Desordenado": "Cabello corto con un estilo texturizado, despeinado y desenfadado en la parte superior, con lados rebajados.",
    "Mechones Largos": "Corte de longitud media con mechones largos y lacios que caen hacia el frente y los lados en forma de cortina.",
    "Corte de Cepillo": "Corte clásico estilo 'crew cut', muy corto y uniforme en los laterales con la parte superior ligeramente más larga.",
    "Peinado Hacia Lado": "Corte clásico formal con una raya lateral bien definida y el cabello perfectamente peinado hacia el costado.",
    "Atrás Desvanecido": "Cabello superior largo y peinado completamente hacia atrás con volumen, acompañado de un degradado limpio en los lados.",
    "Recogido Atrás": "Hombre con cabello largo peinado totalmente hacia atrás y recogido (estilo 'man bun'), con barba corta de pocos días.",

    # --- FILA 2 (Cortes continuos de la fila) ---
    "Cabello Rizado Liso": "Estilo de cabello muy rizado y compacto con gran volumen y forma redondeada (tipo afro corto), etiquetado con esa contradicción en la fila 2.",
    "Militar Corto": "Corte de cabello extremadamente corto y uniforme en toda la cabeza, estilo rapado militar clásico ('buzz cut').",
    "Hacia Arriba": "Cabello corto peinado verticalmente con un acabado texturizado y puntas definidas mediante gel o cera.",
    "Arriba Textura": "Variación de peinado corto hacia arriba con textura desordenada y laterales sutilmente rebajados.",

    # --- FILA 3 ---
    "Mechones Largos 2": "Cabello de longitud media tirando a larga, con ondas naturales que caen de forma relajada a los lados del rostro.",
    "Rizado Liso 2": "Cabello ondulado o rizado de longitud media, peinado con un aspecto natural, suelto y con movimiento.",
    "Afro Largo": "Corte estilo afro clásico de gran tamaño, muy voluminoso, con rizos densos, compactos y forma perfectamente redonda.",
    "Militar Corto 2": "Corte militar muy rebajado y limpio, con contornos de la frente y patillas perfectamente definidos.",
    "Largo de Capas": "Melena larga y lacia que cae por debajo de los hombros, con un corte ligero en capas para dar movimiento.",
    "Desvanecido Bajo": "Corte con un degradado sutil que empieza muy bajo (cerca de las orejas), manteniendo la parte superior corta y prolija.",
    "Casual Texturizado": "Estilo moderno con textura desordenada en la parte superior y laterales cortos, ideal para un look del día a día.",
    "Undercut Peinado": "Laterales muy cortos con una desconexión clara hacia la parte superior, la cual está peinada hacia un lado.",

    # --- FILA 4 ---
    "Corte de Barba 2": "Hombre con una barba completa muy larga y de corte cuadrado, complementada con un corte de cabello muy corto.",
    "Corte de Bargo": "Hombre con barba densa, tupida y bien recortada, combinada con un estilo de cabello corto y peinado formal (etiquetado con error ortográfico de IA).",
    "Desvanecido Bajo 2": "Degradado bajo en las sienes y nuca con el cabello superior denso, corto y peinado hacia adelante.",
    "Desvanecido Bajo 3": "Corte texturizado corto en la parte superior que se va desvaneciendo suavemente hacia los lados (etiquetado 'Desssvanecido Bajo').",
    "Casual Texturizado 2": "Cabello corto con textura suave en la parte superior, peinado hacia el frente de manera casual y relajada.",
    "Clásico Hacia Lado": "Look tradicional, muy pulcro, con raya lateral y el cabello asentado perfectamente con fijador.",
    "Barba Completa": "Hombre con una barba frondosa y larga recortada en forma de pico, combinada con cabello muy corto en la cabeza.",
    "Undercut Peinado 2": "Corte con los laterales muy rebajados y el cabello superior largo y peinado hacia un lado con bastante volumen.",

    # --- ESTILOS COMPLEMENTARIOS (Los 5 que faltaban de la fila 2) ---
    "Estilo 31": "Cabello de longitud media con ondas pronunciadas y volumen natural que enmarca el rostro (Fila 2, posición 1 - 'Cabello Barnas').",
    "Estilo 32": "Corte con degradado limpio en los laterales y cabello corto-medio texturizado en la zona superior (Fila 2, posición 2 - 'Desvanecido').",
    "Estilo 33": "Peinado con los laterales cortos y una cresta más sutil, concentrada hacia la parte frontal y central de la cabeza (Fila 2, posición 3 - 'Cresta Alta').",
    "Estilo 34": "Cabello fijado hacia atrás de forma más plana, combinado con un desvanecido alto en los costados (Fila 2, posición 4 - 'Peinado hacia atrás desvanecido').",
    "Estilo 35": "Rostro femenino con el cabello oscuro completamente recogido hacia atrás en un moño alto (Fila 2, posición 5 - 'Recogido atrás')."
}
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
os.environ["REPLICATE_API_TOKEN"] =  st.secrets["REPLICATE_API_TOKEN"]

def mandar_prompt(imagen_bytes, instruccion_final):
    try:
        prompt_final = (
                f"""A professional studio portrait of the SAME PERSON as in the input image.

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
        """)
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
                        instruccion = f"{catálogo_cortes.get(nombre_corte)}, {color_sel} hair color"
                        st.session_state.resultado = mandar_prompt(archivo.getvalue(), instruccion)

with col_visor:
    st.subheader("✨ Vista Previa")
    if 'resultado' in st.session_state:
        st.image(st.session_state.resultado, use_container_width=True)
        img_data = requests.get(st.session_state.resultado).content
        st.download_button("💾 Guardar Nuevo Look", img_data, "nuevo_corte.png", "image/png")
    else:
        st.info("Subí una foto y elegí un corte del catálogo para ver el resultado.")
