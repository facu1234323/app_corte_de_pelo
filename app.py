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
    "Corte de Barba": (
        "Cabello superior con volumen medio, texturizado hacia arriba y con un sutil direccionamiento "
        "hacia la izquierda. Los laterales presentan un degradado medio (Mid Fade) limpio. Se integra con "
        "una barba completa de alta densidad, con líneas de pómulos perfiladas en diagonal recta, bigote denso "
        "conectado y un acabado cuadrado y simétrico en la zona del mentón."
    ),
    "Cabello Largo": (
        "Melena larga de caída libre que se extiende hasta los hombros, dividida de forma simétrica por una "
        "raya en medio perfectamente definida. Presenta ondas naturales fluidas en el tercio inferior, con "
        "mechones frontales que caen de forma orgánica hacia los lados y puntas texturizadas con movimiento."
    ),
    "Desvanecido": (
        "Vista de perfil que expone un degradado alto (High Fade) pulido al milímetro, que descubre la piel "
        "por encima de la oreja. La zona superior exhibe un copete estilizado (estilo Pompadour) de longitud "
        "media-larga, peinado verticalmente con un sutil quiebre hacia atrás y volumen estructurado desde la raíz."
    ),
    "Cresta Alta": (
        "Corte de estilo Faux Hawk (cresta falsa) de gran impacto. Los paneles laterales se presentan "
        "sumamente cortos con un degradado alto y nítido. El bloque central de cabello se eleva de forma cónica, "
        "convergiendo en puntas afiladas y esculpidas que se proyectan hacia adelante desde la coronilla hasta la frente."
    ),
    "Pelo Corto Desordenado": (
        "Cabello de longitud corta-media con un acabado altamente texturizado y desfilado en la zona superior, "
        "creando mechones multidireccionales con efecto mate y movimiento desenfadado. Los laterales y la nuca "
        "están rebajados a máquina con una transición suave y patillas cortas."
    ),
    "Mechones Largos": (
        "Corte de longitud media de estilo clásico 'curtain haircut' (corte de cortina). El cabello se distribuye "
        "con fluidez hacia ambos lados desde una raya central superior, mostrando mechones lisos y pesados que caen "
        "verticalmente, con las puntas sutilmente desfiladas hacia el interior."
    ),
    "Corte de Cepillo": (
        "Corte estilo Crew Cut de precisión. La zona superior mantiene una longitud corta y uniforme, peinada "
        "levemente hacia el frente con la línea frontal cepillada hacia arriba en un ángulo limpio. Los laterales "
        "y la nuca se desvanecen de forma progresiva con un degradado medio."
    ),
    "Peinado Hacia Lado": (
        "Peinado ejecutivo clásico con una raya lateral izquierda profundamente definida. El bloque de cabello "
        "superior está direccionado de manera impecable hacia la derecha con un acabado pulido, liso y plano. "
        "Los laterales muestran un corte clásico con tijera que disminuye su longitud de forma armónica hacia las orejas."
    ),
    "Atrás Desvanecido": (
        "Estilo Slick Back moderno de alto contraste. El cabello de la zona superior posee una longitud considerable "
        "y se proyecta en su totalidad hacia atrás con volumen controlado y fijación firme. Los laterales están "
        "trabajados con un degradado medio (Mid Fade) que estiliza la estructura craneal."
    ),
    "Recogido Atrás": (
        "Masa capilar larga y densa, traccionada por completo hacia la zona occipital media para formar un "
        "moño recogido (man bun) compacto, limpio y libre de cabellos sueltos. Se complementa en la zona inferior "
        "con una barba corta de tres días de longitud uniforme y contornos naturales."
    ),

    # --- FILA 2 ---
    "Cabello Rizado Liso": (
        "Estructura capilar afro corta y compacta. Presenta una textura de rizos densos, pequeños y cerrados "
        "que se expanden de forma simétrica creando una silueta esférica y uniforme en la parte superior, "
        "acompañada de laterales sutilmente rebajados para mantener la proporción de la corona."
    ),
    "Militar Corto": (
        "Corte Buzz Cut tradicional ejecutado a una longitud ultra corta y uniforme en toda la cabeza (número 1 "
        "o 1.5). Destaca por la máxima precisión geométrica en los contornos, mostrando una línea frontal y sienes "
        "delineadas de forma quirúrgica en ángulos rectos."
    ),
    "Hacia Arriba": (
        "Cabello corto esculpido en picos verticales (estilo Spiky). La zona superior está texturizada en bloques "
        "angulares orientados hacia el centro y arriba con un producto de fijación fuerte. Los laterales muestran "
        "un desvanecido alto con patillas terminadas en punta fina."
    ),
    "Arriba Textura": (
        "Variación de peinado corto elevado. La zona superior presenta un denso trabajo de entresacado que genera "
        "textura en capas cortas, peinadas hacia adelante y hacia arriba en la frente. Los laterales están "
        "recortados limpiamente con una transición sutil de longitud hacia la base."
    ),

    # --- FILA 3 ---
    "Mechones Largos 2": (
        "Cabello de longitud media-larga con una partición orgánica y ligeramente descentrada. Mechones gruesos "
        "con ondas naturales de calibre medio caen libremente hacia los costados superando la línea de la mandíbula, "
        "exhibiendo un volumen fluido, cuerpo y un movimiento natural texturizado."
    ),
    "Rizado Liso 2": (
        "Estilo ondulado de longitud media con textura relajada. El cabello de la parte superior está direccionado "
        "hacia atrás y levemente inclinado a la izquierda, permitiendo que rizos abiertos y bucles suaves se abran "
        "y caigan de manera natural hacia los laterales con volumen ligero."
    ),
    "Afro Largo": (
        "Corte Afro clásico de máxima densidad y volumen. Presenta una distribución geométrica perfectamente esférica "
        "y expandida, estructurada a base de rizos hiper-densos, compactos y elásticos que mantienen una forma "
        "redonda impecable desde cualquier ángulo."
    ),
    "Militar Corto 2": (
        "Corte estilo High and Tight (Alto y Ajustado) de precisión militar. La porción superior es sumamente corta, "
        "plana y compacta, mientras que los laterales y la nuca se conectan de inmediato con un desvanecido total "
        "a la piel (Skin Fade), manteniendo la línea frontal recta."
    ),
    "Largo de Capas": (
        "Melena larga de textura completamente lacia que se extiende por debajo de la línea de los hombros. "
        "Está estructurada mediante un sutil corte en capas en las puntas para aligerar el peso, distribuida "
        "equitativamente a ambos lados a partir de una raya al medio exacta."
    ),
    "Desvanecido Bajo": (
        "Corte de estructura cuadrada en la zona superior, con el cabello corto-medio peinado de manera compacta "
        "hacia el frente y un flequillo recto. Los laterales presentan un degradado bajo (Low Fade) impecable que "
        "limpia exclusivamente el perímetro de la oreja y la nuca baja."
    ),
    "Casual Texturizado": (
        "Corte texturizado de estilo urbano contemporáneo. La corona y la zona superior muestran capas cortas "
        "superpuestas que aportan un volumen desordenado y direccionado hacia el frente en puntas suaves. Los laterales "
        "se mantienen cortos, limpios y pegados al cráneo."
    ),
    "Undercut Peinado": (
        "Corte desconectado de alto contraste. Los laterales y la nuca están rasurados uniformemente a una longitud "
        "mínima sin degradado (Undercut puro), mientras que el bloque superior largo se peina de forma compacta, "
        "plana y pulida hacia el lado derecho, acentuando la línea de desconexión."
    ),

    # --- FILA 4 ---
    "Corte de Barba 2": (
        "Diseño de barba completa de gran longitud, esculpida con líneas de mejilla rectas y un acabado inferior "
        "plano, denso e hiper-perfilado de forma cuadrada. El cabello de la cabeza se mantiene corto, con "
        "textura superior orientada al frente y laterales integrados en degradado hacia la patilla."
    ),
    "Corte de Bargo": (
        "Estructura capilar clásica con cabello superior corto-medio peinado con volumen hacia atrás y sutilmente "
        "hacia la derecha. Se integra de manera fluida con una barba completa de longitud media, densa y con "
        "contornos delineados con precisión tanto en las mejillas como en la línea del cuello."
    ),
    "Desvanecido Bajo 2": (
        "Corte estilo French Crop texturizado. La porción superior se proyecta totalmente hacia adelante, finalizando "
        "en un flequillo corto, denso y de corte horizontal recto en la frente. Los laterales se definen mediante "
        "un degradado bajo que conserva grosor en la zona parietal superior."
    ),
    "Desvanecido Bajo 3": (
        "Corte texturizado corto con picos definidos y desfilados en la zona superior, orientados hacia la frente. "
        "Los laterales y la nuca muestran un degradado bajo-medio (Low-Mid Fade) que limpia las patillas y se conecta "
        "con suavidad hacia la densidad de la coronilla."
    ),
    "Casual Texturizado 2": (
        "Diseño de cabello corto con capas superiores densas trabajadas a tijera para generar una textura suave, "
        "peinada hacia adelante de manera casual y orgánica. Los laterales y contornos están rebajados de forma "
        "uniforme, manteniendo patillas clásicas de grosor medio."
    ),
    "Clásico Hacia Lado": (
        "Peinado formal de etiqueta con una raya lateral izquierda sumamente nítida. El cabello superior está pulido "
        "hacia el lado derecho y ligeramente hacia atrás con un acabado brillante de alta fijación (pomada efecto húmedo). "
        "Los laterales están recortados de manera clásica con tijera sobre peine."
    ),
    "Barba Completa": (
        "Barba majestuosa de gran densidad esculpida geométricamente en forma de cuña o 'pico' pronunciado hacia "
        "el mentón, con líneas de pómulo impecables. El cabello de la cabeza se mantiene extremadamente corto "
        "y degradado a la piel, creando un contraste radical con la opulencia de la barba."
    ),
    "Undercut Peinado 2": (
        "Estructura Undercut de laterales muy rebajados a máquina. El bloque superior, de longitud considerable, "
        "se peina hacia atrás y hacia el lado derecho de forma diagonal, logrando un volumen elevado en la zona del "
        "flequillo mediante técnicas de soplado (secador) y fijación estructurada."
    ),

    # --- ESTILOS COMPLEMENTARIOS (Fila 2, posiciones 1 a 5) ---
    "Estilo 31": (
        "Melena de longitud media con volumen masivo y textura ondulada. Presenta una raya lateral tenue a la derecha, "
        "proyectando ondas y bucles gruesos que caen de forma fluida y pesada hacia el lado izquierdo y hacia atrás, "
        "denotando un movimiento dinámico de gran densidad capilar."
    ),
    "Estilo 32": (
        "Corte Quiff moderno. La zona de la corona se mantiene corta, mientras que el flequillo superior se eleva "
        "con volumen vertical pronunciado, direccionándose hacia atrás y levemente a la derecha. Los laterales "
        "están pulidos con un degradado medio que acentúa la altura del copete frontal."
    ),
    "Estilo 33": (
        "Faux Hawk (cresta) de perfil suavizado. El centro de la zona superior está peinado desde ambos lados hacia "
        "el eje medio, formando una cresta sutil, texturizada y con movimiento inclinado hacia adelante. Los laterales "
        "se presentan cortos con una transición progresiva y limpia hacia las patillas."
    ),
    "Estilo 34": (
        "Peinado Executive Slick Back (peinado formal hacia atrás). El cabello superior es largo y está peinado "
        "completamente hacia atrás de forma compacta y direccional, con una sutil inclinación hacia la derecha. Los "
        "laterales presentan un desvanecido alto que expone limpiamente la zona temporal."
    ),
    "Estilo 35": (
        "Recogido pulido de alta tensión (Top Knot). Toda la masa capilar se encuentra estirada firmemente hacia "
        "atrás de manera completamente simétrica y pegada al cuero cabelludo, concentrándose y sujetándose en un "
        "moño o rodete compacto ubicado exactamente en el vértice superior-posterior del cráneo."
    )
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
