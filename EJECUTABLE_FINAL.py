import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Sistema de Prerrequisitos Académicos", layout="wide")

if "cursos" not in st.session_state:
    st.session_state.cursos = []

if "relaciones" not in st.session_state:
    st.session_state.relaciones = []


def agregar_curso(curso):
    curso = curso.strip()

    if curso == "":
        return False, "Ingrese un nombre de curso."

    if curso in st.session_state.cursos:
        return False, "El curso ya existe."

    st.session_state.cursos.append(curso)
    return True, "Curso agregado correctamente."


def genera_ciclo(origen, destino):
    G = nx.DiGraph()

    for c in st.session_state.cursos:
        G.add_node(c)

    for a, b in st.session_state.relaciones:
        G.add_edge(a, b)

    if origen in G and destino in G:
        return nx.has_path(G, destino, origen)

    return False


def agregar_relacion(origen, destino):

    if origen == "" or destino == "":
        return False, "Seleccione ambos cursos."

    if origen == destino:
        return False, "Un curso no puede depender de sí mismo."

    relacion = (origen, destino)

    if relacion in st.session_state.relaciones:
        return False, "La relación ya existe."

    if genera_ciclo(origen, destino):
        return False, "La relación genera una dependencia circular."

    st.session_state.relaciones.append(relacion)
    return True, "Prerrequisito agregado correctamente."


def calcular_hasse(R):

    H = []

    for i in range(len(R)):
        H.append(R[i])

    i = 0

    while i < len(H):

        if H[i][0] == H[i][1]:
            H.pop(i)

        else:
            i += 1

    i = 0

    while i < len(H):

        a = H[i][0]
        b = H[i][1]

        eliminar = False

        for j in range(len(H)):

            if H[j][0] == a and H[j][1] != b:

                c = H[j][1]

                for k in range(len(H)):

                    if H[k][0] == c and H[k][1] == b:
                        eliminar = True

        if eliminar:
            H.pop(i)

        else:
            i += 1

    return H


def generar_figura_digrafo():

    G = nx.DiGraph()

    for curso in st.session_state.cursos:
        G.add_node(curso)

    for origen, destino in st.session_state.relaciones:
        G.add_edge(origen, destino)

    fig, ax = plt.subplots(figsize=(8, 6))

    pos = nx.spring_layout(G, seed=42)

    nx.draw(
        G,
        pos,
        with_labels=True,
        arrows=True,
        node_size=3000,
        font_size=8,
        ax=ax
    )

    ax.set_title("Dígrafo de prerrequisitos")

    return fig


def generar_figura_hasse():

    H = calcular_hasse(st.session_state.relaciones)

    G = nx.DiGraph()

    for curso in st.session_state.cursos:
        G.add_node(curso)

    for origen, destino in H:
        G.add_edge(origen, destino)

    niveles = {}

    for curso in st.session_state.cursos:
        niveles[curso] = 0

    cambio = True

    while cambio:

        cambio = False

        for a, b in H:

            if niveles[b] <= niveles[a]:

                niveles[b] = niveles[a] + 1
                cambio = True

    capas = {}

    for nodo in niveles:

        nivel = niveles[nodo]

        if nivel not in capas:
            capas[nivel] = []

        capas[nivel].append(nodo)

    pos = {}

    for nivel in capas:

        nodos = capas[nivel]

        for i in range(len(nodos)):

            x = i - (len(nodos) - 1) / 2
            y = nivel

            pos[nodos[i]] = (x, y)

    fig, ax = plt.subplots(figsize=(8, 6))

    nx.draw(
        G,
        pos,
        with_labels=True,
        arrows=False,
        node_size=3000,
        font_size=8,
        ax=ax
    )

    ax.set_title("Diagrama de Hasse")

    return fig


st.title("SISTEMA DE PRERREQUISITOS ACADÉMICOS")

st.subheader("Registro de cursos")

curso = st.text_input("Nombre del curso")

if st.button("Agregar Curso"):
    ok, mensaje = agregar_curso(curso)

    if ok:
        st.success(mensaje)
    else:
        st.error(mensaje)

st.subheader("Registro de prerrequisitos")

if len(st.session_state.cursos) >= 2:

    col1, col2 = st.columns(2)

    with col1:
        origen = st.selectbox("Curso origen", st.session_state.cursos)

    with col2:
        destino = st.selectbox("Curso destino", st.session_state.cursos)

    if st.button("Agregar Prerrequisito"):
        ok, mensaje = agregar_relacion(origen, destino)

        if ok:
            st.success(mensaje)
        else:
            st.error(mensaje)

else:
    st.info("Debe registrar al menos dos cursos.")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Cursos")
    for curso in st.session_state.cursos:
        st.write("•", curso)

with c2:
    st.subheader("Prerrequisitos")
    for origen, destino in st.session_state.relaciones:
        st.write(f"{origen} → {destino}")

st.divider()

v1, v2 = st.columns(2)

with v1:

    st.subheader("Dígrafo")

    if len(st.session_state.relaciones) > 0:

        fig = generar_figura_digrafo()

        st.pyplot(fig)

        buffer = BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)

        st.download_button(
            "Descargar Dígrafo PNG",
            data=buffer,
            file_name="digrafo.png",
            mime="image/png"
        )

with v2:

    st.subheader("Diagrama de Hasse")

    if len(st.session_state.relaciones) > 0:

        fig_h = generar_figura_hasse()

        st.pyplot(fig_h)

        buffer_h = BytesIO()
        fig_h.savefig(buffer_h, format="png", bbox_inches="tight")
        buffer_h.seek(0)

        st.download_button(
            "Descargar Hasse PNG",
            data=buffer_h,
            file_name="hasse.png",
            mime="image/png"
        )

if st.button("Limpiar Todo"):

    st.session_state.cursos = []
    st.session_state.relaciones = []

    st.rerun()
