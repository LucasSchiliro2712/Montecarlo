
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
from io import BytesIO

# -----------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------

st.set_page_config(
    page_title="Método de Monte Carlo",
    page_icon="🔵",
    layout="wide"
)

st.title("🎯 Aproximación de π mediante Monte Carlo")

st.write(
    "Experimentá con diferentes radios y cantidades de puntos "
    "para observar cómo se aproxima el valor de π."
)

# -----------------------------------
# PANEL DE CONFIGURACIÓN
# -----------------------------------

st.sidebar.header("Configuración")

r = st.sidebar.number_input(
    "Radio de la circunferencia",
    min_value=0.1,
    max_value=1000.0,
    value=1.0,
    step=0.5
)

n = st.sidebar.number_input(
    "Cantidad de puntos aleatorios",
    min_value=100,
    max_value=1000000,
    value=10000,
    step=1000
)

# -----------------------------------
# FUNCIONES
# -----------------------------------

def pertenece_al_circulo(x, y, r):
    return x**2 + y**2 <= r**2


def generar_puntos(n, r):
    x = np.random.uniform(-r, r, n)
    y = np.random.uniform(-r, r, n)

    dentro = pertenece_al_circulo(x, y, r)

    return x, y, dentro


def aproximar_pi(dentro):
    return 4 * np.mean(dentro)


# -----------------------------------
# GENERACIÓN DE GRÁFICOS
# -----------------------------------

if st.sidebar.button("Generar gráficos", type="primary"):

    with st.spinner("Generando puntos y gráficos..."):

        # Generamos todos los puntos
        x, y, dentro = generar_puntos(int(n), r)

        # Aproximación final
        pi_aprox = aproximar_pi(dentro)

        error = abs(pi_aprox - math.pi) / math.pi * 100

        # -----------------------------------
        # GRÁFICO 1: CONVERGENCIA DE PI
        # -----------------------------------

        acumulados = np.cumsum(dentro)

        cantidades = np.unique(
            np.geomspace(1, int(n), min(150, int(n))).astype(int)
        )

        aproximaciones = (
            4 * acumulados[cantidades - 1] / cantidades
        )

        fig1, ax1 = plt.subplots(figsize=(9, 5))

        ax1.plot(
            cantidades,
            aproximaciones,
            color="royalblue",
            label="Aproximación de π"
        )

        ax1.axhline(
            y=math.pi,
            color="red",
            linestyle="--",
            label="Valor real de π"
        )

        ax1.set_xscale("log")
        ax1.set_xlabel("Cantidad de puntos (escala logarítmica)")
        ax1.set_ylabel("Valor aproximado de π")
        ax1.set_title("Convergencia del método de Monte Carlo")
        ax1.grid(alpha=0.3)
        ax1.legend()

        # Guardamos el gráfico 1
        buffer1 = BytesIO()
        fig1.savefig(buffer1, format="png", dpi=200, bbox_inches="tight")
        buffer1.seek(0)

        st.session_state["grafico1"] = buffer1.getvalue()
        plt.close(fig1)

        # -----------------------------------
        # GRÁFICO 2: REPRESENTACIÓN GEOMÉTRICA
        # -----------------------------------

        fig2, ax2 = plt.subplots(figsize=(7, 7))

        # Dibujamos el cuadrado
        cuadrado = plt.Rectangle(
            (-r, -r),
            2*r,
            2*r,
            fill=False,
            color="black",
            linewidth=2
        )

        ax2.add_patch(cuadrado)

        # Dibujamos la circunferencia
        circulo = plt.Circle(
            (0, 0),
            r,
            fill=False,
            color="red",
            linewidth=2
        )

        ax2.add_patch(circulo)

        # Para evitar sobrecargar el gráfico,
        # mostramos como máximo 20.000 puntos.
        cantidad_grafico = min(int(n), 20000)

        indices = np.random.choice(
            int(n),
            size=cantidad_grafico,
            replace=False
        )

        # Puntos dentro del círculo
        ax2.scatter(
            x[indices][dentro[indices]],
            y[indices][dentro[indices]],
            color="royalblue",
            s=5,
            label="Dentro del círculo"
        )

        # Puntos fuera del círculo
        ax2.scatter(
            x[indices][~dentro[indices]],
            y[indices][~dentro[indices]],
            color="orange",
            s=5,
            label="Fuera del círculo"
        )

        ax2.set_xlim(-r*1.1, r*1.1)
        ax2.set_ylim(-r*1.1, r*1.1)
        ax2.set_aspect("equal")

        ax2.set_xlabel("Eje X")
        ax2.set_ylabel("Eje Y")
        ax2.set_title("Distribución de puntos aleatorios")
        ax2.grid(alpha=0.2)
        ax2.legend()

        # Guardamos el gráfico 2
        buffer2 = BytesIO()
        fig2.savefig(buffer2, format="png", dpi=200, bbox_inches="tight")
        buffer2.seek(0)

        st.session_state["grafico2"] = buffer2.getvalue()
        plt.close(fig2)

        # Guardamos los resultados
        st.session_state["pi_aprox"] = pi_aprox
        st.session_state["error"] = error
        st.session_state["total"] = int(n)
        st.session_state["dentro"] = int(np.sum(dentro))
        st.session_state["fuera"] = int(n - np.sum(dentro))


# -----------------------------------
# MOSTRAR RESULTADOS
# -----------------------------------

if "grafico1" in st.session_state:

    st.divider()

    st.subheader("Resultados de la simulación")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "π aproximado",
        f"{st.session_state['pi_aprox']:.6f}"
    )

    col2.metric(
        "Valor real de π",
        f"{math.pi:.6f}"
    )

    col3.metric(
        "Error porcentual",
        f"{st.session_state['error']:.4f}%"
    )

    st.write(
        f"**Puntos dentro:** {st.session_state['dentro']:,}  |  "
        f"**Puntos fuera:** {st.session_state['fuera']:,}  |  "
        f"**Total:** {st.session_state['total']:,}"
    )

    st.divider()

    # GRÁFICO 1

    st.subheader("1. Aproximación de π")

    st.image(st.session_state["grafico1"])

    st.download_button(
        label="⬇️ Descargar gráfico 1",
        data=st.session_state["grafico1"],
        file_name="aproximacion_pi.png",
        mime="image/png"
    )

    st.divider()

    # GRÁFICO 2

    st.subheader("2. Distribución geométrica de los puntos")

    st.image(st.session_state["grafico2"])

    st.download_button(
        label="⬇️ Descargar gráfico 2",
        data=st.session_state["grafico2"],
        file_name="distribucion_puntos.png",
        mime="image/png"
    )

else:

    st.info(
        "Seleccioná los parámetros en el panel izquierdo "
        "y presioná 'Generar gráficos' para comenzar."
    )
