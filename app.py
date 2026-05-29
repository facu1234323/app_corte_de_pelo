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
        "ESTILO: Modern Quiff con Mid Fade integrado a barba regia. "
        "DIRECCIÓN: Proyección vertical con torsión oblicua hacia la izquierda en el flequillo. "
        "TIPO DE PELO: Lacio, grosor medio, densidad folicular alta. "
        "LONGITUD Y ALTURA: Superior media-larga (6-7 cm), laterales desvanecidos desde el 1.5 al 3. "
        "TEXTURA Y COLOR: Acabado mate, texturizado seco; color negro azabache. "
        "ELEGANCIA Y DESTINO: Elegancia vanguardista. Ideal para entornos urbanos premium, "
        "industrias creativas y eventos nocturnos formales que requieran distinción moderna."
    ),
    "Cabello Largo": (
        "ESTILO: Melena Completa Clásica (Classic Mane). "
        "DIRECCIÓN: Caída libre bilateral con distribución simétrica desde una raya al medio exacta. "
        "TIPO DE PELO: Ondulado leve (2A), grosor fino-medio, densidad media con excelente caída. "
        "LONGITUD Y ALTURA: Cabello largo homogéneo que alcanza la base de los trapecios (25-30 cm). "
        "TEXTURA Y COLOR: Textura sedosa con brillo natural; color castaño oscuro profundo. "
        "ELEGANCIA Y DESTINO: Elegancia bohemia e intelectual. Perfecto para entornos artísticos, "
        "galerías de arte, desfiles de moda y eventos de etiqueta alternativa o casual premium."
    ),
    "Desvanecido": (
        "ESTILO: Executive Pompadour con High Fade (Desvanecido Alto). "
        "DIRECCIÓN: Elevación frontal de raíz y direccionamiento curvo hacia la zona occipital. "
        "TIPO DE PELO: Lacio rígido, grosor grueso, densidad muy alta. "
        "LONGITUD Y ALTURA: Bloque superior largo (8-10 cm), laterales rasurados con técnica skin fade que expone la zona parietal superior. "
        "TEXTURA Y COLOR: Acabado ultra pulido con pomada de fijación fuerte y brillo medio; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Máxima elegancia corporativa. Diseñado para reuniones de alta dirección, bodas de gala y entornos financieros de etiqueta estricta."
    ),
    "Cresta Alta": (
        "ESTILO: Avant-Garde Faux Hawk (Cresta Falsa Estilizada). "
        "DIRECCIÓN: Convergencia bilateral hacia el eje central con proyección apical hacia adelante. "
        "TIPO DE PELO: Lacio grueso con alta resiliencia y memoria de fijación. "
        "LONGITUD Y ALTURA: Corona central de longitud decreciente (de 7 cm al frente a 3 cm en coronilla), laterales con desvanecido alto al número 0. "
        "TEXTURA Y COLOR: Textura esculpida en picos definidos, acabado mate; color negro carbón. "
        "ELEGANCIA Y DESTINO: Elegancia disruptiva y urbana. Destinado a alfombras rojas de la cultura pop, eventos de moda urbana y perfiles deportivos de alto nivel."
    ),
    "Pelo Corto Desordenado": (
        "ESTILO: Messy Textured Crop. "
        "DIRECCIÓN: Multidireccional y desestructurado en la corona, con el flequillo ligeramente orientado al frente. "
        "TIPO DE PELO: Lacio o levemente ondulado, grosor medio, densidad media-alta. "
        "LONGITUD Y ALTURA: Superior corto-medio (4-5 cm) entresacado con tijera de esculpir; laterales cónicos rebajados a máquina al número 2. "
        "TEXTURA Y COLOR: Textura desfilada, aspecto orgánico y mate; color castaño oscuro natural. "
        "ELEGANCIA Y DESTINO: Elegancia casual informal. Ideal para el día a día, ambientes universitarios, agencias de publicidad y código de vestimenta smart-casual relajado."
    ),
    "Mechones Largos": (
        "ESTILO: Classic Curtain Haircut (Corte de Cortina noventero). "
        "DIRECCIÓN: Apertura simétrica en forma de arco desde la línea media, cayendo hacia los pómulos. "
        "TIPO DE PELO: Lacio dócil, grosor fino, densidad media con caída pesada. "
        "LONGITUD Y ALTURA: Longitud media (12-14 cm) en la zona del flequillo, disminuyendo sutilmente hacia la nuca media. "
        "TEXTURA Y COLOR: Acabado satinado, suave y sin peso; color castaño oscuro con reflejos fríos. "
        "ELEGANCIA Y DESTINO: Elegancia juvenil y sofisticada. Va perfecto en pasarelas, producciones fotográficas, eventos de diseño y ambientes semi-formales relajados."
    ),
    "Corte de Cepillo": (
        "ESTILO: Precision Crew Cut (Corte de Cepillo Americano). "
        "DIRECCIÓN: Peinado sutilmente hacia el frente con la línea frontal cepillada verticalmente a 90 grados. "
        "TIPO DE PELO: Lacio y extremadamente grueso/rebelde, densidad folicular muy alta. "
        "LONGITUD Y ALTURA: Zona superior ultra corta y decreciente (de 2.5 cm a 1 cm), laterales con desvanecido medio (Mid Fade). "
        "TEXTURA Y COLOR: Textura densa, compacta y uniforme de acabado limpio; color negro. "
        "ELEGANCIA Y DESTINO: Elegancia minimalista y atlética. Ideal para el ámbito deportivo de élite, cuerpos de seguridad, negocios tradicionales o climas cálidos de alta exigencia."
    ),
    "Peinado Hacia Lado": (
        "ESTILO: Traditional Side Part (Raya al Lado Ejecutiva). "
        "DIRECCIÓN: Partición profunda en el lado izquierdo y direccionamiento chato y pulido hacia el lado derecho. "
        "TIPO DE PELO: Lacio u ondulado fino, grosor medio, densidad alta controlada. "
        "LONGITUD Y ALTURA: Longitud superior media (6 cm) acoplada a la curvatura craneal, laterales clásicos pulidos a tijera sobre peine (número 3-4). "
        "TEXTURA Y COLOR: Textura húmeda y compacta, fijación con gomina de alto brillo; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia clásica impecable. Excelente para bodas tradicionales, audiencias legales, diplomacia y cenas de gala benéficas."
    ),
    "Atrás Desvanecido": (
        "ESTILO: Modern Slick Back con Mid Fade. "
        "DIRECCIÓN: Peinado unidireccional recto hacia la nuca con sobreelevación volumétrica en el área frontal. "
        "TIPO DE PELO: Lacio dócil o moldeado, grosor medio-grueso, densidad alta. "
        "LONGITUD Y ALTURA: Superior largo (9-11 cm) para asegurar la transición, laterales con desvanecido medio pulido. "
        "TEXTURA Y COLOR: Acabado semibrillante, peinado con peine de dientes anchos que marca líneas; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia contemporánea de alto impacto. Destinado a cenas de negocios VIP, galas nocturnas modernas y entornos cosmopolitas sofisticados."
    ),
    "Recogido Atrás": (
        "ESTILO: Sleek Man Bun (Moño Alto Recogido). "
        "DIRECCIÓN: Tracción total concéntrica de 360 grados orientada hacia el vértice superior-occipital. "
        "TIPO DE PELO: Lacio u ondulado largo, grosor medio, alta densidad capilar. "
        "LONGITUD Y ALTURA: Longitud extrema unificada (mínimo 20 cm) comprimida en un rodete compacto; laterales limpios. "
        "TEXTURA Y COLOR: Superficie craneal pulida y libre de frizz, acabado satinado natural; color negro profundo. "
        "ELEGANCIA Y DESTINO: Elegancia alternativa minimalista. Va orientado a eventos de alta moda, festivales de cine, entornos corporativos modernos/tech y situaciones casuales elegantes."
    ),

    # --- FILA 2 ---
    "Cabello Rizado Liso": (
        "ESTILO: Compact Rounded Afro. "
        "DIRECCIÓN: Expansión radial multidireccional tridimensional (3D) desde el cuero cabelludo. "
        "TIPO DE PELO: Rizado afro muy cerrado (4C), grosor grueso, densidad folicular extrema. "
        "LONGITUD Y ALTURA: Longitud uniforme corta (3-4 cm) esculpida geométricamente en silueta esférica. "
        "TEXTURA Y COLOR: Textura esponjosa, opaca y densa de alta absorción lumínica; color negro azabache. "
        "ELEGANCIA Y DESTINO: Elegancia étnica urbana refinada. Perfecto para presentaciones artísticas, desfiles de street-wear de lujo y eventos culturales de gala."
    ),
    "Militar Corto": (
        "ESTILO: High Geometric Buzz Cut. "
        "DIRECCIÓN: Sin dirección (longitud menor al límite de peinado), totalmente uniforme. "
        "TIPO DE PELO: Indistinto, ideal para cabellos gruesos y densos que marcan la línea de implantación. "
        "LONGITUD Y ALTURA: Rapado milimétrico general (número 1), con contornos periféricos rectificados con navaja (Line-Up). "
        "TEXTURA Y COLOR: Textura rasposa, micro-texturizada, acabado mate absoluto; color negro. "
        "ELEGANCIA Y DESTINO: Elegancia minimalista y severa. Adecuado para un estilo de vida de alto rendimiento, militares, deportistas de combate o pasarelas de vanguardia industrial."
    ),
    "Hacia Arriba": (
        "ESTILO: Textured Spiky Hair con High Fade. "
        "DIRECCIÓN: Elevación verticalizada e individualizada de mechones en la cúspide craneal. "
        "TIPO DE PELO: Lacio rebelde o grueso con gran soporte estructural. "
        "LONGITUD Y ALTURA: Superior corto-medio (4-5 cm) desfilado en puntas, laterales desvanecidos al cero alto. "
        "TEXTURA Y COLOR: Textura puntiaguda definida con cera de arcilla (Clay) de acabado extra mate; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia juvenil dinámica. Diseñado para clubes nocturnos premium, eventos informales de alta gama y perfiles del mundo del entretenimiento."
    ),
    "Arriba Textura": (
        "ESTILO: Modern Textured Top con Taper Fade. "
        "DIRECCIÓN: Direccionamiento hacia adelante superpuesto en capas con flequillo elevado en la punta. "
        "TIPO DE PELO: Lacio u ondulado, grosor medio, densidad alta que requiere control de peso. "
        "LONGITUD Y ALTURA: Zona superior media (5-6 cm) con entresacado profundo, laterales limpios con conicidad baja. "
        "TEXTURA Y COLOR: Textura desordenada y fragmentada, acabado mate natural; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia urbana contemporánea. Muy versátil, ideal para ejecutivos jóvenes, agencias de marketing y viajes de negocios en fines de semana."
    ),

    # --- FILA 3 ---
    "Mechones Largos 2": (
        "ESTILO: Mid-Length Wavy Flow. "
        "DIRECCIÓN: Caída natural libre hacia los laterales a partir de una raya desestructurada y sutilmente ladeada. "
        "TIPO DE PELO: Ondulado con cuerpo (2B), grosor medio, densidad media con volumen elástico. "
        "LONGITUD Y ALTURA: Longitud media extendida (15-18 cm) sobrepasando el plano de los lóbulos auriculares. "
        "TEXTURA Y COLOR: Textura ondulada definida con crema de peinado, brillo natural; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia informal distinguida. Va dirigido a resorts de lujo, eventos de polo/náutica, cenas al aire libre y ambientes creativos de alto standing."
    ),
    "Rizado Liso 2": (
        "ESTILO: Messy Layered Waves. "
        "DIRECCIÓN: Desplazamiento oblicuo hacia atrás y hacia el lateral izquierdo con volumen fluido. "
        "TIPO DE PELO: Ondulado cerrado o rizado abierto (2C/3A), grosor medio, densidad media-alta. "
        "LONGITUD Y ALTURA: Superior de longitud media (8-10 cm) en capas decrecientes hacia los lados y nuca baja. "
        "TEXTURA Y COLOR: Textura de bucles sueltos, acabado hidratado con volumen ligero; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia casual refinada. Ideal para el sector de la moda, eventos sociales semi-formales de tarde y entornos profesionales con códigos flexibles."
    ),
    "Afro Largo": (
        "ESTILO: Majestic Large Afro (Afro Esférico de Gran Volumen). "
        "DIRECCIÓN: Proyección radial omnidireccional masiva desde el epicentro del cuero cabelludo. "
        "TIPO DE PELO: Rizado helicoidal denso (4A/4B), grosor medio, densidad folicular masiva. "
        "LONGITUD Y ALTURA: Longitud unificada de gran formato (12-15 cm de radio periférico uniforme). "
        "TEXTURA Y COLOR: Textura algodonosa, compacta y esponjosa de alta opacidad; color negro mate. "
        "ELEGANCIA Y DESTINO: Máxima elegancia cultural e identitaria. Ideal para galas artísticas internacionales, eventos de activismo premium y galas de diseño independiente."
    ),
    "Militar Corto 2": (
        "ESTILO: High and Tight Flattop. "
        "DIRECCIÓN: Estructura plana superior horizontal (Flat-Top) sin dirección de peinado. "
        "TIPO DE PELO: Lacio ultra grueso de alta rigidez vertical. "
        "LONGITUD Y ALTURA: Superior extremadamente corta e idéntica en nivel horizontal (1.5 cm), laterales rasurados a piel (Skin Fade) altos. "
        "TEXTURA Y COLOR: Textura milimétrica, densa, compacta, acabado mate; color negro. "
        "ELEGANCIA Y DESTINO: Elegancia rígida y disciplinada. Adecuado para perfiles corporativos de seguridad corporativa, atletas de alto rendimiento o eventos temáticos retro-futuristas."
    ),
    "Largo de Capas": (
        "ESTILO: Long Layered Straight Hair. "
        "DIRECCIÓN: Caída vertical plomada y rectilínea distribuida simétricamente desde una raya central. "
        "TIPO DE PELO: Lacio absoluto (1A), grosor medio-grueso, densidad alta con caída pesada. "
        "LONGITUD Y ALTURA: Longitud muy larga que sobrepasa las clavículas (35 cm) con capas invisibles en los extremos. "
        "TEXTURA Y COLOR: Textura ultra lisa, pulida, con alta refracción lumínica (brillante); color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia vanguardista y andrógina. Perfecto para el sector del modelaje de alta costura, eventos de gala de diseño industrial y alfombras rojas."
    ),
    "Desvanecido Bajo": (
        "ESTILO: Modern French Crop con Low Fade. "
        "DIRECCIÓN: Proyección unificada hacia el frente culminando en un flequillo horizontal romo sobre la frente. "
        "TIPO DE PELO: Lacio denso, grosor medio-grueso, implantación frontal baja. "
        "LONGITUD Y ALTURA: Superior corto-medio (4-5 cm) denso, laterales limpios con degradado bajo que bordea solo la oreja. "
        "TEXTURA Y COLOR: Textura maciza y compacta de bloque, acabado mate; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia urbana minimalista. Ideal para diseñadores gráficos, arquitectos, eventos de cultura digital y el día a día smart-casual de oficina moderna."
    ),
    "Casual Texturizado": (
        "ESTILO: Textured Short Caesar Cut. "
        "DIRECCIÓN: Peinado hacia el frente en capas cortas entrelazadas con flequillo texturizado irregular. "
        "TIPO DE PELO: Lacio u ondulado, grosor fino-medio, densidad media. "
        "LONGITUD Y ALTURA: Superior corto (3-4 cm) vaciado con navaja, laterales cónicos cortos integrados al número 2. "
        "TEXTURA Y COLOR: Textura plumosa con micro-capas, acabado mate con volumen aireado; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia práctica y funcional. Excelente para el ritmo diario de negocios, ejecutivos comerciales en constante movimiento y ambientes corporativos relajados."
    ),
    "Undercut Peinado": (
        "ESTILO: Disconnected Undercut con Side Sweep. "
        "DIRECCIÓN: Barrido lateral compacto hacia la derecha con desconexión total respecto al panel parietal. "
        "TIPO DE PELO: Lacio dócil, grosor medio, densidad alta que permite un aplastamiento pulcro. "
        "LONGITUD Y ALTURA: Superior largo (8-10 cm), laterales y nuca rasurados uniformemente a máquina al número 1 sin degradar (bloque sólido). "
        "TEXTURA Y COLOR: Textura lisa, compacta, acabado satinado con pomada clásica; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia hípster/alternativa sofisticada. Destinado a inauguraciones de locales premium, festivales de diseño y reuniones sociales vanguardistas."
    ),

    # --- FILA 4 ---
    "Corte de Barba 2": (
        "ESTILO: Heavy Beard Styling con Short Crop. "
        "DIRECCIÓN: Superior peinado hacia adelante con elevación milimétrica en el nacimiento del flequillo. "
        "TIPO DE PELO: Lacio grueso en cabeza, cabello de barba de densidad extrema y patrón rizado denso. "
        "LONGITUD Y ALTURA: Cabello muy corto (3 cm), barba de gran formato esculpida a 10 cm con base horizontal plana. "
        "TEXTURA Y COLOR: Textura superior mate y compacta; barba hidratada con aceite, acabado pulcro; color negro. "
        "ELEGANCIA Y DESTINO: Elegancia rústica premium (Lumbersexual de lujo). Va perfecto para barberías boutique, eventos gastronómicos gourmet y convenciones de negocios de industrias tradicionales."
    ),
    "Corte de Bargo": (
        "ESTILO: Classic Executive Contour con Barba Completa Media. "
        "DIRECCIÓN: Diagonal hacia atrás y levemente hacia el lado derecho con volumen sutil en el copete. "
        "TIPO DE PELO: Lacio u ondulado grueso, densidad folicular alta y homogénea. "
        "LONGITUD Y ALTURA: Superior medio (5-6 cm), laterales rebajados con tijera en técnica clásica, barba de 3 cm cuadrada. "
        "TEXTURA Y COLOR: Acabado natural de fijación flexible (cera base agua), brillo bajo; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia tradicional señorial. Perfecto para directores de empresas, cenas de gala benéficas, clubes de campo y ambientes profesionales conservadores."
    ),
    "Desvanecido Bajo 2": (
        "ESTILO: Heavy Textured Crop con Low Skin Fade. "
        "DIRECCIÓN: Direccionamiento masivo hacia adelante desde la coronilla con flequillo recto texturizado. "
        "TIPO DE PELO: Lacio hiper-denso, grosor muy grueso, alta resistencia. "
        "LONGITUD Y ALTURA: Bloque superior de 5 cm con peso visual, laterales desvanecidos a piel exclusivamente en el perímetro bajo. "
        "TEXTURA Y COLOR: Textura pesada y aserrada en las puntas, acabado mate tiza; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia urbana contemporánea de alta fidelidad. Ideal para productores musicales, fotógrafos de moda y eventos de arte contemporáneo de vanguardia."
    ),
    "Desvanecido Bajo 3": (
        "ESTILO: Short Spiky Caesar con Drop Fade. "
        "DIRECCIÓN: Peinado hacia el frente con puntas desfiladas hacia arriba en la línea frontal. "
        "TIPO DE PELO: Lacio rígido, grosor medio, densidad alta con nacimiento hacia adelante. "
        "LONGITUD Y ALTURA: Superior corto (3-4 cm) entresacado, laterales degradados con caída curva detrás de la oreja (Drop Fade). "
        "TEXTURA Y COLOR: Textura de picos suaves dispersos, acabado mate; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia casual dinámica y deportiva. Ideal para viajes, actividades físicas de alto rendimiento y el día a día en oficinas tecnológicas."
    ),
    "Casual Texturizado 2": (
        "ESTILO: Organic Short Layers (Corte Clásico Texturizado Suave). "
        "DIRECCIÓN: Peinado sutil hacia adelante con caída natural y orgánica de los mechones en la frente. "
        "TIPO DE PELO: Lacio fino o medio, dócil, densidad media que busca volumen visual. "
        "LONGITUD Y ALTURA: Superior medio-corto (4 cm) cortado enteramente a tijera, laterales clásicos cónicos al número 3. "
        "TEXTURA Y COLOR: Textura suave, fluida y con movimiento libre, acabado natural sin producto pesado; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia sobria, discreta y cotidiana (estilo 'Quiet Luxury'). Perfecto para profesionales de la salud, académicos, reuniones familiares elegantes y el día a día de oficina."
    ),
    "Clásico Hacia Lado": (
        "ESTILO: Wet-Look Gentleman's Part (Peinado de Época Impecable). "
        "DIRECCIÓN: Raya lateral izquierda nítida trazada con peine; bloque superior direccionado a la derecha en plano perfecto. "
        "TIPO DE PELO: Lacio dócil, grosor fino o medio, densidad alta controlada. "
        "LONGITUD Y ALTURA: Superior medio (5-6 cm) adaptado al cráneo, laterales pulidos de forma clásica decreciente con tijera. "
        "TEXTURA Y COLOR: Textura hiper-compacta de efecto espejo, acabado de brillo húmedo (pomada al óleo); color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Máxima elegancia histórica/formal. Es el corte por excelencia para bodas de etiqueta formal (Black Tie), óperas, recepciones diplomáticas y eventos históricos."
    ),
    "Barba Completa": (
        "ESTILO: Extreme Contrast (Skin Fade Alto con Barba de Cuña). "
        "DIRECCIÓN: Cabello superior inexistente por rapado absoluto; barba con peinado vertical descendente hacia el pico del mentón. "
        "TIPO DE PELO: Cabello ausente (calvicie intencional o rapado); barba hiper-densa, gruesa y compacta. "
        "LONGITUD Y ALTURA: Cabeza al número 0 (cuchilla/shaver), barba de gran formato (12-14 cm) perfilada en punta afilada. "
        "TEXTURA Y COLOR: Cuero cabelludo pulido satinado; barba tratada con bálsamo de brillo moderado; color negro con matices. "
        "ELEGANCIA Y DESTINO: Elegancia audaz y masculina de alto perfil. Diseñado para entornos VIP nocturnos, empresarios del sector del entretenimiento de lujo y eventos de moda transgresora."
    ),
    "Undercut Peinado 2": (
        "ESTILO: Voluminous Overcut (Pompadour Desconectado). "
        "DIRECCIÓN: Proyección en diagonal hacia atrás y a la derecha con gran elevación neumática (volumen por secador) en el frente. "
        "TIPO DE PELO: Lacio grueso o moldeado con volumen natural, densidad alta. "
        "LONGITUD Y ALTURA: Superior extra largo (10-12 cm) para generar el arco del copete; laterales con undercut rasurado corto uniforme. "
        "TEXTURA Y COLOR: Textura aireada pero firme, fijación con laca mate de alta resistencia; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia audaz de alta costura. Ideal para estilistas, diseñadores de interiores, galas de premios modernos y eventos nocturnos de alta alcurnia cosmopolita."
    ),

    # --- ESTILOS COMPLEMENTARIOS (Fila 2, posiciones 1 a 5) ---
    "Estilo 31": (
        "ESTILO: Long Wavy Flow con Raya Lateral (Estilo 'Mane'). "
        "DIRECCIÓN: Partición difusa a la derecha, proyectando una gran masa capilar ondulada hacia la izquierda y atrás. "
        "TIPO DE PELO: Ondulado grueso (2B/2C), gran resiliencia y volumen nativo. "
        "LONGITUD Y ALTURA: Longitud larga-media (18-20 cm) que cubre totalmente las orejas y cae hacia la nuca. "
        "TEXTURA Y COLOR: Textura salvaje controlada con crema hidratante, acabado satinado; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia bohemia sofisticada y seductora. Ideal para eventos de gala informales en la playa, festivales de música clásica contemporánea y cócteles de tarde."
    ),
    "Estilo 32": (
        "ESTILO: Textured Modern Quiff. "
        "DIRECCIÓN: Elevación frontal pronunciada de atrás hacia adelante con el flequillo que quiebra hacia atrás en la punta. "
        "TIPO DE PELO: Lacio u ondulado, grosor medio, densidad alta con buena elasticidad de raíz. "
        "LONGITUD Y ALTURA: Superior largo en la sección frontal (7-8 cm) decreciendo a la coronilla; laterales con degradado medio. "
        "TEXTURA Y COLOR: Textura dinámica con hilos definidos, acabado mate con polvos de volumen; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia casual refinada y juvenil. Va excelente para directores de startups tecnológicas, agencias de publicidad exclusivas y cenas formales de fin de semana."
    ),
    "Estilo 33": (
        "ESTILO: Soft Faux Hawk (Cresta Urbana Suave). "
        "DIRECCIÓN: Orientación sutil de los laterales superiores hacia el centro, creando un lomo texturizado lineal. "
        "TIPO DE PELO: Lacio medio, densidad alta con buena respuesta a ceras de fijación media. "
        "LONGITUD Y ALTURA: Eje central de 5 cm, reduciendo sutilmente en los laterales parietales altos; degradado medio cónico. "
        "TEXTURA Y COLOR: Textura entrelazada desordenada, acabado mate natural; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia casual de fin de semana. Adecuado para almuerzos ejecutivos casuales, viajes de descanso premium y eventos recreativos exclusivos."
    ),
    "Estilo 34": (
        "ESTILO: Slick Back High Fade (Peinado Hacia Atrás Formal Moderno). "
        "DIRECCIÓN: Peinado unidireccional plano y compacto hacia atrás con sutil desviación diagonal a la derecha. "
        "TIPO DE PELO: Lacio, grosor medio, densidad alta. "
        "LONGITUD Y ALTURA: Superior largo (8-9 cm) pegado al cráneo, laterales con desvanecido alto pulido desde el cero. "
        "TEXTURA Y COLOR: Textura compacta y uniforme, fijado con cera pomada de brillo medio; color castaño oscuro. "
        "ELEGANCIA Y DESTINO: Elegancia corporativa agresiva y moderna. Perfecto para el sector inmobiliario de lujo, finanzas de Wall Street, casinos premium y eventos formales nocturnos."
    ),
    "Estilo 35": (
        "ESTILO: Avant-Garde High Top Knot (Moño Alto de Pasarela). "
        "DIRECCIÓN: Máxima tracción simétrica de tensión hacia la cúspide (corona alta) de la cabeza. "
        "TIPO DE PELO: Lacio absoluto, grosor fino-medio, alta densidad capilar. "
        "LONGITUD Y ALTURA: Longitud larga (mínimo 22 cm) compactada en un mini moño esférico pulcro en la cima; laterales tirantes. "
        "TEXTURA Y COLOR: Textura pulida efecto cristal, libre de imperfecciones, fijación extrema con laca brillante; color negro profundo. "
        "ELEGANCIA Y DESTINO: Elegancia conceptual/editorial máxima. Exclusivo para pasarelas internacionales de alta costura, eventos artísticos de élite, inauguraciones de arquitectura de vanguardia y entornos andróginos de lujo."
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
