import streamlit as st
from modulo_curso_superior import renderizar_modulo_curso_superior

st.set_page_config(
    page_title="Números que Falam: Descobrindo o Brasil (IBGE)",
    page_icon="📊",
    layout="wide"
)

st.sidebar.title("🧭 Navegação do Painel IBGE")
indicador = st.sidebar.radio(
    "Selecione o Indicador Demográfico:",
    [
        "2. Curso Superior (STEM & Talentos)",
        "1. Afazeres Domésticos (Módulo do Grupo)",
        "3. Crescimento Demográfico (Módulo do Grupo)",
        "4. IDH / IDHM Municipal (Módulo do Grupo)",
        "5. Transporte e Mobilidade (Módulo do Grupo)",
        "6. Trabalho e Emprego (Módulo do Grupo)"
    ]
)

st.sidebar.markdown("---")

if indicador.startswith("2. Curso Superior"):
    renderizar_modulo_curso_superior()
else:
    st.info(f"🚧 Espaço reservado para integrar o código do integrante responsável por: **{indicador}**.")
