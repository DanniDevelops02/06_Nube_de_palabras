import io
import re
import unicodedata
import zlib
from collections import Counter
from html import escape

import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import streamlit as st
from wordcloud import STOPWORDS, WordCloud

st.set_page_config(
    page_title="Nube de palabras · Daniel Flórez",
    page_icon="☁️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# =====================================================================
#  CONTENIDO
# =====================================================================
EJEMPLOS = {
    "Inteligencia artificial": (
        "La inteligencia artificial es una disciplina de la informática orientada a "
        "desarrollar sistemas capaces de ejecutar tareas que requieren capacidades "
        "cognitivas humanas. El aprendizaje automático, las redes neuronales profundas y "
        "el procesamiento del lenguaje natural constituyen los pilares técnicos de los "
        "sistemas modernos de inteligencia artificial. Los modelos de lenguaje de gran "
        "escala, la visión computacional y la robótica autónoma representan aplicaciones "
        "de vanguardia. La inteligencia artificial transforma sectores como la salud, la "
        "educación, la manufactura, las finanzas y el transporte, generando eficiencias "
        "significativas."
    ),
    "Colombia": (
        "Colombia es una nación situada en el extremo noroccidental de América del Sur, "
        "reconocida por su excepcional biodiversidad, riqueza cultural y diversidad de "
        "paisajes. Bogotá es la capital y principal centro económico, seguida de Medellín, "
        "Cali y Barranquilla como ciudades de relevancia nacional. El café colombiano goza "
        "de reconocimiento internacional por su calidad y perfil aromático. La floricultura "
        "colombiana abastece mercados globales con alta competitividad. El país alberga "
        "ecosistemas del Amazonas, los Andes, el Caribe y el Pacífico, constituyéndose como "
        "uno de los territorios con mayor biodiversidad del planeta."
    ),
    "Tecnología 4.0": (
        "La cuarta revolución industrial redefine los modelos productivos mediante la "
        "convergencia de tecnologías digitales avanzadas. El Internet de las cosas, la "
        "inteligencia artificial, el análisis de grandes datos, la robótica colaborativa y "
        "la automatización inteligente son pilares estratégicos de la industria moderna. "
        "Las fábricas inteligentes integran sensores, conectividad y analítica para "
        "optimizar procesos en tiempo real. La manufactura aditiva, los gemelos digitales "
        "y la realidad aumentada transforman la ingeniería de producción. La computación en "
        "la nube y la ciberseguridad son habilitadores fundamentales de la transformación "
        "digital empresarial."
    ),
}

# Paletas pensadas para fondo claro. En fondo oscuro se aclaran solas.
PALETAS = {
    "Océano": ["#3f71a6", "#1b2f45", "#2d5a8a", "#5b8fc2", "#16456e", "#7aa6d1"],
    "Marino profundo": ["#04152a", "#0d2e5b", "#1b4d8f", "#3886e1", "#2a6bbf", "#0a2342"],
    "Hielo y menta": ["#2b8a9e", "#3f71a6", "#4fa3a5", "#1b6b7a", "#78c2c4", "#5b8fc2"],
    "Índigo": ["#312e81", "#3730a3", "#4338ca", "#4f46e5", "#6366f1", "#1e1b4b"],
    "Grafito": ["#111827", "#1f2937", "#374151", "#4b5563", "#6b7280", "#0f172a"],
    "Terracota": ["#7c2d12", "#9a3412", "#c2410c", "#ea580c", "#f97316", "#b45309"],
}

FORMAS = ["Rectángulo", "Círculo", "Nube", "Corazón"]

FONDOS_NUBE = {
    "Claro": "#ffffff",
    "Oscuro": "#0d2e5b",
    "Transparente": None,
}

# Fondo de página tipo cuaderno: (imagen del patrón, tamaño del patrón)
PATRONES = {
    "Puntos": (
        "radial-gradient(circle, rgba(63,113,166,.30) 1.5px, transparent 1.7px)",
        "26px 26px",
    ),
    "Rayas": (
        "linear-gradient(rgba(63,113,166,.20) 1px, transparent 1px)",
        "100% 34px",
    ),
    "Cuadrícula": (
        "linear-gradient(rgba(63,113,166,.16) 1px, transparent 1px), "
        "linear-gradient(90deg, rgba(63,113,166,.16) 1px, transparent 1px)",
        "28px 28px, 28px 28px",
    ),
    "Liso": (None, None),
}

# =====================================================================
#  ESTILO (paleta fría basada en #3f71a6)
# =====================================================================
PRIMARIO = "#3f71a6"
OSCURO = "#1b2f45"
CLARO = "#eaf2f9"
SUAVE = "#a9c7e3"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600&family=Playfair+Display:wght@500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
    font-size: 1.06rem;
}
.stApp { background-color: #f6fafd; __PATRON__ }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 940px; padding-top: 3rem; padding-bottom: 4rem; }

/* Hero */
.hero { text-align: center; padding: 1rem 0 .5rem 0; }
.hero .etiqueta {
    font-family: 'Caveat', cursive; font-size: 1.8rem; font-weight: 600;
    color: __PRIMARIO__; line-height: 1;
}
.hero h1 {
    font-family: 'Playfair Display', serif; font-size: 3.3rem; color: __OSCURO__;
    margin: .3rem 0 .6rem 0; line-height: 1.1;
}
.hero h1 span {
    background: linear-gradient(transparent 62%, rgba(169, 199, 227, .75) 62%);
    padding: 0 .12em;
}
.hero p { color: #4d6479; font-size: 1.2rem; max-width: 620px; margin: 0 auto; }
.linea {
    width: 70px; height: 4px; border-radius: 4px; background: __PRIMARIO__;
    margin: 1.4rem auto;
}
h2, h3 { font-family: 'Playfair Display', serif !important; color: __OSCURO__ !important; }

/* Tarjetas con "cinta washi" */
[data-testid="stVerticalBlockBorderWrapper"] {
    position: relative;
    overflow: visible;
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1px solid __SUAVE__66 !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 24px rgba(63, 113, 166, .08);
    padding: .6rem .8rem;
}
[data-testid="stVerticalBlockBorderWrapper"]::before {
    content: "";
    position: absolute;
    top: -9px; left: 28px;
    width: 78px; height: 18px;
    background: rgba(169, 199, 227, .7);
    border-radius: 2px;
    transform: rotate(-1.5deg);
    box-shadow: 0 1px 2px rgba(27, 47, 69, .08);
    z-index: 1;
}

/* Imagen de la nube */
[data-testid="stImage"] img { border-radius: 14px; }

/* Métricas */
[data-testid="stMetric"], [data-testid="metric-container"] {
    background: white; border: 1px dashed __SUAVE__; border-radius: 14px;
    padding: 12px 16px;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif; color: __OSCURO__; font-weight: 600;
}
[data-testid="stMetricLabel"] { color: #6b8399; }

/* Barras de frecuencia */
.freq-row {
    display: flex; align-items: center; gap: 12px;
    padding: 7px 12px; margin: 5px 0;
    background: #f6fafd; border: 1px dashed __SUAVE__; border-radius: 10px;
}
.freq-row .rank {
    font-family: 'IBM Plex Mono', monospace; font-size: .78rem; font-weight: 500;
    color: #6b8399; min-width: 34px;
}
.freq-row .palabra { font-weight: 600; color: __OSCURO__; min-width: 110px; }
.freq-row .barra {
    flex: 1; height: 8px; background: __CLARO__; border-radius: 4px; overflow: hidden;
}
.freq-row .barra > div { height: 100%; background: __PRIMARIO__; border-radius: 4px; }
.freq-row .num {
    font-family: 'IBM Plex Mono', monospace; font-size: .88rem; color: __OSCURO__;
    min-width: 28px; text-align: right;
}

/* Bloques informativos */
.info-item {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 16px; margin-bottom: 8px;
    background: #f6fafd; border: 1px dashed __SUAVE__; border-radius: 12px;
}
.info-item strong { color: __OSCURO__; }
.info-item p { margin: 2px 0 0 0; color: #4d6479; font-size: .92rem; }
.uso-tag {
    display: inline-block; background: white; border: 1px dashed __SUAVE__;
    border-radius: 999px; padding: 5px 14px; margin: 4px 3px;
    font-size: .88rem; font-weight: 500; color: __OSCURO__;
}
.texto-procesado {
    font-family: 'IBM Plex Mono', monospace; font-size: .85rem; line-height: 1.8;
    color: __OSCURO__; background: #f6fafd; border: 1px dashed __SUAVE__;
    border-radius: 12px; padding: 16px;
}

/* Botones */
.stButton > button, .stDownloadButton > button {
    background: __PRIMARIO__; color: white; border: 1.5px solid __PRIMARIO__;
    border-radius: 999px; padding: .65rem 1.6rem; font-size: 1.02rem; font-weight: 600;
    transition: all .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: __OSCURO__; border-color: __OSCURO__; color: white;
    transform: translateY(-2px); box-shadow: 0 8px 18px rgba(27, 47, 69, .25);
}
[data-testid="stBaseButton-secondary"] { background: white; color: __PRIMARIO__; }

/* Inputs */
.stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
    border-radius: 12px; border: 1px solid __SUAVE__; font-size: 1.02rem;
}
[data-testid="stFileUploaderDropzone"] {
    background: __CLARO__; border: 2px dashed __SUAVE__; border-radius: 16px;
}
[data-testid="stAlert"] { border-radius: 14px; }

/* Sidebar */
[data-testid="stSidebar"] { background: __OSCURO__; }
[data-testid="stSidebar"] * { color: #e6f0f9 !important; }

#MainMenu, footer { visibility: hidden; }
</style>
"""


def construir_css(patron: str) -> str:
    imagen, tamano = PATRONES[patron]
    base = "linear-gradient(180deg, #f6fafd 0%, #eaf2f9 100%)"
    if imagen:
        fondo = f"background-image: {imagen}, {base}; background-size: {tamano}, 100% 100%;"
    else:
        fondo = f"background-image: {base};"
    css = CSS.replace("__PATRON__", fondo)
    for token, valor in {
        "__PRIMARIO__": PRIMARIO,
        "__OSCURO__": OSCURO,
        "__CLARO__": CLARO,
        "__SUAVE__": SUAVE,
    }.items():
        css = css.replace(token, valor)
    return css


# =====================================================================
#  LÓGICA: LIMPIEZA Y ANÁLISIS DE TEXTO
# =====================================================================
PATRON_PALABRA = r"[^\W\d_]+"  # letras de cualquier idioma (con tildes, ñ, etc.)


def normalizar(palabra: str) -> str:
    """Quita tildes para comparar (conserva la ñ): 'más' y 'mas' son la misma."""
    nfd = unicodedata.normalize("NFD", palabra)
    sin_marcas = re.sub(r"(?<!n)[\u0300-\u036f]", "", nfd)
    return unicodedata.normalize("NFC", sin_marcas)


_STOPWORDS_ES = """
a al algo algún alguna algunas alguno algunos allá allí ante antes aquel aquella aquellas
aquello aquellos aquí así aun aún aunque bajo cada casi como con contra cual cuales cuando
cuanto cuyo da dan de del demás dentro desde después donde dos durante e el ella ellas ello
ellos en entonces entre era eran eres es esa esas ese eso esos esta está estaba estaban
estado estamos están estar estas este esto estos estoy fue fueron fui ha había habían haber
habrá han hasta hay he hecho hemos hace hacen hacer hacia incluso ir la las le les lo los
luego mas más me mediante mientras mi mis mismo misma mismos mismas mucha muchas mucho
muchos muy nada ni no nos nosotros nuestra nuestras nuestro nuestros nunca o os otra otras
otro otros para pero poco pocos podemos poder podía puede pueden puedo pues que qué quien
quienes quién se sea sean según ser será serán sería si sí siempre siendo sido sin sino sobre
solo sólo son soy su sus tal tales también tampoco tan tanto te tener tenemos tenía tiene
tienen tengo ti todavía todo todos tras tu tú tus un una uno unos usted ustedes va van
varias varios vez voy vosotros y ya yo
"""

SW_ES = {normalizar(p) for p in _STOPWORDS_ES.split()}
SW_EN = {normalizar(p.lower()) for p in STOPWORDS}


def stopwords_para(idioma: str) -> set:
    if idioma == "Español":
        return SW_ES
    if idioma == "Inglés":
        return SW_EN
    if idioma == "Ambos":
        return SW_ES | SW_EN
    return set()


def detectar_idioma(texto: str) -> str:
    palabras = [normalizar(p) for p in re.findall(PATRON_PALABRA, texto.lower())]
    es = sum(p in SW_ES for p in palabras)
    en = sum(p in SW_EN for p in palabras)
    return "Español" if es >= en else "Inglés"


def tokenizar(texto: str, stopwords: set, min_longitud: int) -> list:
    """Devuelve las palabras útiles: sin enlaces, números, stopwords ni palabras cortas."""
    texto = re.sub(r"https?://\S+|www\.\S+", " ", texto.lower())
    palabras = re.findall(PATRON_PALABRA, texto)
    return [p for p in palabras if len(p) >= min_longitud and normalizar(p) not in stopwords]


def estadisticas(texto: str) -> dict:
    todas = re.findall(PATRON_PALABRA, texto.lower())
    n = len(todas)
    unicas = len(set(todas))
    oraciones = len([s for s in re.split(r"[.!?…]+", texto) if s.strip()])
    minutos = n / 200
    return {
        "palabras": n,
        "oraciones": oraciones,
        "unicas": unicas,
        "riqueza": unicas / n if n else 0,
        "longitud_media": sum(len(p) for p in todas) / n if n else 0,
        "lectura": "< 1 min" if minutos < 1 else f"{round(minutos)} min",
    }


def decodificar(datos: bytes) -> str:
    for codificacion in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return datos.decode(codificacion)
        except UnicodeDecodeError:
            continue
    return datos.decode("utf-8", errors="ignore")


# =====================================================================
#  LÓGICA: NUBE DE PALABRAS
# =====================================================================
def crear_mascara(forma: str):
    """Máscara para WordCloud: 255 = fuera de la forma, 0 = dentro."""
    if forma == "Rectángulo":
        return None

    if forma == "Círculo":
        n = 600
        y, x = np.ogrid[:n, :n]
        dentro = (x - n / 2) ** 2 + (y - n / 2) ** 2 <= (n / 2 - 8) ** 2

    elif forma == "Nube":
        w, h = 1000, 600
        y, x = np.ogrid[:h, :w]

        def circulo(cx, cy, r):
            return (x - cx) ** 2 + (y - cy) ** 2 <= r**2

        dentro = (
            circulo(250, 400, 160)
            | circulo(750, 400, 160)
            | circulo(500, 300, 230)
            | circulo(360, 270, 150)
            | circulo(650, 270, 150)
            | ((x >= 250) & (x <= 750) & (y >= 400) & (y <= 560))
        )

    else:  # Corazón
        n = 600
        y, x = np.ogrid[:n, :n]
        cx = (x - n / 2) / (n * 0.36)
        cy = -(y - n * 0.47) / (n * 0.36)
        dentro = (cx**2 + cy**2 - 1) ** 3 - cx**2 * cy**3 <= 0

    return np.where(dentro, 0, 255).astype(np.uint8)


def aclarar(color_hex: str, cantidad: float = 0.45) -> str:
    """Mezcla un color con blanco (para que se lea sobre fondo oscuro)."""
    r, g, b = (int(color_hex[i : i + 2], 16) for i in (1, 3, 5))
    r, g, b = (round(c + (255 - c) * cantidad) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


@st.cache_data(show_spinner=False, max_entries=30)
def generar_nube(frecuencias: tuple, paleta: str, fondo: str, forma: str, max_words: int) -> bytes:
    """Genera la nube y la devuelve como PNG. El resultado queda en caché."""
    color_fondo = FONDOS_NUBE[fondo]
    colores = PALETAS[paleta]
    if fondo == "Oscuro":
        colores = [aclarar(c) for c in colores]

    def color_func(word, **kwargs):
        # El color depende de la palabra, así la nube se ve igual cada vez
        return colores[zlib.crc32(word.encode("utf-8")) % len(colores)]

    fuente = fm.findfont(fm.FontProperties(family="DejaVu Sans", weight="bold"))
    nube = WordCloud(
        width=1000,
        height=600,
        mask=crear_mascara(forma),
        background_color=color_fondo,
        mode="RGB" if color_fondo else "RGBA",
        color_func=color_func,
        font_path=fuente,
        max_words=max_words,
        min_font_size=10,
        max_font_size=140,
        prefer_horizontal=0.8,
        relative_scaling=0.5,
        margin=4,
        scale=2,
        random_state=42,
    ).generate_from_frequencies(dict(frecuencias))

    buffer = io.BytesIO()
    nube.to_image().save(buffer, format="PNG")
    return buffer.getvalue()


# =====================================================================
#  CALLBACKS
# =====================================================================
def cargar_ejemplo():
    st.session_state["texto"] = EJEMPLOS[st.session_state["ejemplo_sel"]]


# =====================================================================
#  PÁGINA
# =====================================================================
with st.sidebar:
    st.subheader("Cómo usarlo")
    st.markdown(
        "1. Escribe, pega o sube un texto.\n"
        "2. Ajusta idioma, paleta y forma de la nube.\n"
        "3. Mira la nube, las estadísticas y las palabras más frecuentes.\n"
        "4. Descarga la imagen o la tabla."
    )
    st.subheader("Estilo de la página")
    patron = st.radio(
        "Fondo de cuaderno",
        list(PATRONES),
        horizontal=True,
        label_visibility="collapsed",
    )

st.markdown(construir_css(patron), unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <div class="etiqueta">cuaderno de análisis de texto ✎</div>
        <h1>Nube de <span>palabras</span></h1>
        <p>Pega un texto y descubre de un vistazo cuáles son sus palabras clave.</p>
        <div class="linea"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- 1. Texto ----
texto_input = ""
with st.container(border=True):
    st.subheader("1 · Tu texto")
    fuente = st.radio(
        "Fuente del texto",
        ["✍️ Escribir o pegar", "📂 Subir archivo"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if fuente.startswith("✍️"):
        st.text_area(
            "Texto",
            key="texto",
            height=190,
            placeholder="Pega aquí un artículo, una reseña, un discurso, respuestas de una encuesta...",
            label_visibility="collapsed",
        )
        texto_input = st.session_state.get("texto", "")
        c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
        with c1:
            st.selectbox("Texto de ejemplo", list(EJEMPLOS), key="ejemplo_sel")
        with c2:
            st.button("Cargar", on_click=cargar_ejemplo, use_container_width=True)

    else:
        archivo = st.file_uploader(
            "Archivo de texto",
            type=["txt", "md", "csv"],
            label_visibility="collapsed",
        )
        if archivo is not None:
            contenido = decodificar(archivo.getvalue())
            if archivo.name.lower().endswith(".csv"):
                try:
                    tabla = pd.read_csv(io.StringIO(contenido), sep=None, engine="python")
                except Exception:
                    try:
                        tabla = pd.read_csv(io.StringIO(contenido))
                    except Exception as error:
                        tabla = None
                        st.error(f"No se pudo leer el CSV. ({error})")
                if tabla is not None and not tabla.empty:
                    columnas = list(tabla.columns)
                    candidatas = [c for c in columnas if not pd.api.types.is_numeric_dtype(tabla[c])]
                    por_defecto = columnas.index(candidatas[0]) if candidatas else 0
                    columna = st.selectbox("Columna de texto", columnas, index=por_defecto)
                    texto_input = " . ".join(tabla[columna].dropna().astype(str).tolist())
            else:
                texto_input = contenido
            if texto_input:
                st.success(f"Archivo cargado: {len(texto_input):,} caracteres.")

st.write("")

# ---- 2. Ajustes ----
with st.container(border=True):
    st.subheader("2 · Ajustes")
    a1, a2 = st.columns(2)
    with a1:
        idioma_sel = st.selectbox(
            "Palabras vacías (stopwords)",
            ["Automático", "Español", "Inglés", "Ambos", "Ninguno"],
            help="Son palabras muy comunes (el, de, the, and...) que no aportan significado.",
        )
    with a2:
        min_longitud = st.slider("Longitud mínima de palabra", 2, 8, 3)
    palabras_extra = st.text_input(
        "Excluir palabras adicionales",
        placeholder="ej: gracias, hola, señor",
    )
    b1, b2 = st.columns(2)
    with b1:
        paleta_sel = st.selectbox("Paleta de colores", list(PALETAS))
    with b2:
        forma_sel = st.selectbox("Forma de la nube", FORMAS)
    b3, b4 = st.columns(2)
    with b3:
        fondo_sel = st.radio("Fondo de la nube", list(FONDOS_NUBE), horizontal=True)
    with b4:
        max_words = st.slider("Máximo de palabras", 20, 200, 80)

st.write("")

# ---- Sin texto: pantalla de bienvenida ----
if not texto_input.strip():
    with st.container(border=True):
        st.subheader("¿Qué es una nube de palabras?")
        st.write(
            "Es una imagen donde las palabras más frecuentes de un texto aparecen más "
            "grandes. Sirve para identificar los temas centrales de un vistazo."
        )
        for icono, titulo, desc in [
            ("📊", "Análisis de frecuencia", "Cuenta qué palabras y pares de palabras dominan el texto."),
            ("🔍", "Filtrado inteligente", "Quita palabras vacías en español e inglés, con o sin tildes."),
            ("🎨", "Personalización", "Elige paleta, forma (círculo, nube, corazón) y fondo."),
            ("⬇️", "Exportación", "Descarga la nube en PNG y la tabla de frecuencias en CSV."),
        ]:
            st.markdown(
                f'<div class="info-item"><span style="font-size:1.3rem">{icono}</span>'
                f"<div><strong>{titulo}</strong><p>{desc}</p></div></div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            "".join(
                f'<span class="uso-tag">{caso}</span>'
                for caso in [
                    "📰 Prensa y noticias",
                    "📋 Encuestas abiertas",
                    "💬 Reseñas de clientes",
                    "🎓 Textos académicos",
                    "🗳️ Discursos",
                    "📚 Estudios literarios",
                ]
            ),
            unsafe_allow_html=True,
        )
        st.caption("Carga un texto de ejemplo en el paso 1 para empezar.")
    st.stop()

# ---- Procesamiento ----
idioma_real = detectar_idioma(texto_input) if idioma_sel == "Automático" else idioma_sel
stopwords = set(stopwords_para(idioma_real))
stopwords |= {
    normalizar(p.strip().lower())
    for p in re.split(r"[,;\n]", palabras_extra)
    if p.strip()
}

palabras = tokenizar(texto_input, stopwords, min_longitud)
if not palabras:
    st.error(
        "No quedaron palabras después de la limpieza. Reduce la longitud mínima o cambia "
        "la configuración de stopwords."
    )
    st.stop()

conteo = Counter(palabras)
frecuentes = conteo.most_common()
df_freq = pd.DataFrame(frecuentes[:50], columns=["Palabra", "Frecuencia"])
stats = estadisticas(texto_input)

# ---- 3. Nube ----
with st.container(border=True):
    st.subheader("3 · Tu nube de palabras")
    if idioma_sel == "Automático":
        st.caption(f"Idioma detectado para las stopwords: {idioma_real}.")
    try:
        with st.spinner("Generando la nube..."):
            png = generar_nube(
                tuple(frecuentes[:max_words]), paleta_sel, fondo_sel, forma_sel, max_words
            )
        st.image(png, use_container_width=True)
        st.download_button(
            "Descargar imagen PNG",
            data=png,
            file_name="nube_de_palabras.png",
            mime="image/png",
            use_container_width=True,
        )
    except Exception as error:
        st.error(f"No se pudo generar la nube. ({error})")

st.write("")

# ---- 4. Estadísticas ----
with st.container(border=True):
    st.subheader("4 · Análisis del texto")
    m1, m2, m3 = st.columns(3)
    m1.metric("Palabras", f"{stats['palabras']:,}")
    m2.metric("Oraciones", f"{stats['oraciones']:,}")
    m3.metric("Palabras únicas", f"{stats['unicas']:,}")
    m4, m5, m6 = st.columns(3)
    m4.metric("Riqueza léxica", f"{stats['riqueza']:.0%}")
    m5.metric("Longitud media", f"{stats['longitud_media']:.1f} letras")
    m6.metric("Tiempo de lectura", stats["lectura"])
    st.caption(
        f"Tras la limpieza quedan {len(palabras):,} palabras útiles y "
        f"{len(conteo):,} distintas. La riqueza léxica es el porcentaje de palabras "
        "únicas sobre el total."
    )

st.write("")

# ---- 5. Frecuencias ----
with st.container(border=True):
    st.subheader("5 · Frecuencias")
    tab_palabras, tab_pares, tab_texto = st.tabs(
        ["📊 Palabras", "🔗 Pares de palabras", "🧾 Texto procesado"]
    )

    with tab_palabras:
        col_barras, col_tabla = st.columns(2, gap="large")
        with col_barras:
            top = df_freq.head(15)
            maximo = int(top["Frecuencia"].max())
            filas = []
            for rank, (palabra, frecuencia) in enumerate(top.itertuples(index=False), 1):
                porcentaje = max(6, round(100 * frecuencia / maximo))
                filas.append(
                    f'<div class="freq-row"><span class="rank">#{rank:02d}</span>'
                    f'<span class="palabra">{escape(palabra)}</span>'
                    f'<div class="barra"><div style="width:{porcentaje}%"></div></div>'
                    f'<span class="num">{int(frecuencia)}</span></div>'
                )
            st.markdown("".join(filas), unsafe_allow_html=True)
        with col_tabla:
            st.dataframe(
                df_freq,
                use_container_width=True,
                hide_index=True,
                height=430,
                column_config={
                    "Frecuencia": st.column_config.ProgressColumn(
                        "Frecuencia",
                        min_value=0,
                        max_value=int(df_freq["Frecuencia"].max()),
                        format="%d",
                    )
                },
            )
            st.download_button(
                "Exportar tabla (.csv)",
                data=pd.DataFrame(frecuentes, columns=["Palabra", "Frecuencia"])
                .to_csv(index=False)
                .encode("utf-8"),
                file_name="frecuencias.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with tab_pares:
        pares = Counter(zip(palabras, palabras[1:]))
        repetidos = [(f"{a} {b}", n) for (a, b), n in pares.most_common(20) if n >= 2]
        if repetidos:
            df_pares = pd.DataFrame(repetidos, columns=["Par de palabras", "Veces"])
            st.dataframe(
                df_pares,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Veces": st.column_config.ProgressColumn(
                        "Veces",
                        min_value=0,
                        max_value=int(df_pares["Veces"].max()),
                        format="%d",
                    )
                },
            )
            st.caption("Son palabras que aparecen juntas, una tras otra, después de la limpieza.")
        else:
            st.info("Ningún par de palabras se repite. Prueba con un texto más largo.")

    with tab_texto:
        vista = " ".join(palabras)
        recorte = vista[:2500] + ("..." if len(vista) > 2500 else "")
        st.markdown(f'<div class="texto-procesado">{escape(recorte)}</div>', unsafe_allow_html=True)

st.write("")
st.caption("Nube generada con la librería wordcloud.")
