import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Estadísticas de Carros Dylan", layout="wide")

# CSS personalizado para quitar el borde del formulario y el texto de ayuda
st.markdown("""
    <style>
    [data-testid="stForm"] {
        border: 0px !important;
        padding: 0px !important;
    }
    [data-testid="InputInstructions"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal de la aplicación
st.title("Estadísticas de Carros Dylan")

# URL de tu dataset en GitHub
DATA_URL = "https://raw.githubusercontent.com/dylsaac/Carros-y-Marcas/main/cars_information.csv"

# Función para cargar los datos con caché
@st.cache_data
def cargar_datos():
    data = pd.read_csv(DATA_URL)
    return data

df_original = cargar_datos()

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.header("Búsqueda Chida")

# Checkbox para mostrar todos los datos
mostrar_todos = st.sidebar.checkbox("Mostrar todos los datos", value=False)

# Inicializar estado para el buscador
if 'modelo_query' not in st.session_state:
    st.session_state.modelo_query = ""

# 1. Buscador de modelo dentro de un formulario sin bordes
with st.sidebar.form(key='form_busqueda_modelo'):
    temp_modelo = st.text_input("Modelo del carro:", value=st.session_state.modelo_query)
    btn_buscar = st.form_submit_button("Buscar")
    if btn_buscar:
        st.session_state.modelo_query = temp_modelo

# 2. Selector de marca ('car_make') insensible a mayúsculas/minúsculas
marcas = ["Todas"]
if 'car_make' in df_original.columns:
    marcas_unicas = df_original['car_make'].dropna().astype(str).str.strip().unique()
    marcas = ["Todas"] + sorted(list(marcas_unicas), key=lambda x: str(x).lower())
    
seleccion_marca = st.sidebar.selectbox("Seleccionar marca / categoría:", marcas)

# Detectar columnas numéricas para las gráficas y el filtro de precios
columnas_numericas = df_original.select_dtypes(include=['number']).columns.tolist()

# 3. Buscador de precios con dos barras (Valor mínimo y Valor máximo)
with st.sidebar.expander("Buscador de precios"):
    st.write("Rango de precios")
    
    col_precio = 'car_price' if 'car_price' in df_original.columns else (columnas_numericas[0] if len(columnas_numericas) > 0 else None)
    
    filtro_min, filtro_max = None, None
    if col_precio and not df_original.empty:
        precios_validos = pd.to_numeric(df_original[col_precio], errors='coerce').dropna()
        if not precios_validos.empty:
            min_posible = float(precios_validos.min())
            max_posible = float(precios_validos.max())
            
            if min_posible < max_posible:
                filtro_min = st.slider("Valor mínimo", min_posible, max_posible, min_posible)
                filtro_max = st.slider("Valor máximo", min_posible, max_posible, max_posible)

# ==========================================
# LÓGICA DE FILTRADO ROBUSTA
# ==========================================
if mostrar_todos:
    df_filtrado = df_original.copy()
else:
    df_filtrado = df_original.copy()
    
    # Aplicar filtro de modelo
    if st.session_state.modelo_query and 'car_model' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['car_model'].astype(str).str.contains(st.session_state.modelo_query, case=False, na=False)]
        
    # Aplicar filtro de marca (insensible a mayúsculas/minúsculas)
    if seleccion_marca != "Todas" and 'car_make' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['car_make'].astype(str).str.strip().str.lower() == seleccion_marca.strip().lower()]
        
    # Aplicar filtro de precios
    if col_precio and filtro_min is not None and filtro_max is not None:
        df_filtrado = df_filtrado[(pd.to_numeric(df_filtrado[col_precio], errors='coerce') >= filtro_min) & 
                                  (pd.to_numeric(df_filtrado[col_precio], errors='coerce') <= filtro_max)]

# ==========================================
# CUERPO PRINCIPAL - TABLA Y GRÁFICAS
# ==========================================
if mostrar_todos:
    st.subheader("Todos los datos")
    st.dataframe(df_filtrado)
else:
    st.subheader("Datos filtrados")
    st.dataframe(df_filtrado.head(10))

# Validar si hay suficientes columnas numéricas para las gráficas
if len(columnas_numericas) >= 2:
    col1 = columnas_numericas[0]
    col2 = columnas_numericas[1]

    # 1. Histograma (Sin cuadrícula)
    st.subheader(f"Histograma: {col1}")
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    if not df_filtrado.empty:
        df_filtrado[col1].dropna().hist(ax=ax1, bins=15, color='tab:blue', edgecolor='black')
    ax1.set_xlabel(col1)
    ax1.set_ylabel("Frecuencia")
    ax1.grid(False)
    st.pyplot(fig1)

    # 2. Gráfica de Dispersión (Sin cuadrícula)
    st.subheader(f"Dispersión: {col1} vs {col2}")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    if not df_filtrado.empty:
        ax2.scatter(df_filtrado[col1], df_filtrado[col2], alpha=0.7, color='tab:blue')
    ax2.set_xlabel(col1)
    ax2.set_ylabel(col2)
    ax2.grid(False)
    st.pyplot(fig2)

    # 3. Gráfica de Líneas (Sin cuadrícula)
    st.subheader(f"Gráfica de Líneas: Frecuencia de {col1}")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    if not df_filtrado.empty:
        conteo = df_filtrado[col1].value_counts().sort_index()
        ax3.plot(conteo.index, conteo.values, marker='o', linestyle='-', color='tab:blue')
    ax3.set_xlabel(col1)
    ax3.set_ylabel("Cantidad")
    ax3.grid(False)
    st.pyplot(fig3)
else:
    st.warning("El dataset necesita al menos dos columnas numéricas para generar todas las gráficas correctamente.")

# ==========================================
# SECCIÓN FINAL Y MAPA
# ==========================================
st.write("Acerca de:")
st.write("Matrícula: S26004642")
st.write("Alumno: Dylan Heredia Rodriguez")
st.write("Ciudad: OrizabaYork")
st.write("Aura: Exceso")
st.write("Guapura: 100%")

# Mapa con las coordenadas proporcionadas (sin usar pydeck)
df_coordenadas = pd.DataFrame({
    'lat': [18.838957844015003],
    'lon': [-97.11625838791207]
})
st.map(df_coordenadas)

st.write("P.D Los de Gestion no la arman.")