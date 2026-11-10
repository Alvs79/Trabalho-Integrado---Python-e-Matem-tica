import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from gerar_base_curso_superior import criar_base_curso_superior

@st.cache_data
def carregar_dados_padrao():
    if not os.path.exists("dados_curso_superior_ibge.csv"):
        return criar_base_curso_superior()
    return pd.read_csv("dados_curso_superior_ibge.csv")

def higienizar_dados(df):
    """Pipeline ETL: Limpeza de nulos, padronização de tipos e colunas."""
    df = df.copy()
    df.columns = [col.strip() for col in df.columns]
    colunas_obrigatorias = ["Ano", "UF", "Area_Conhecimento", "Sexo", "Taxa_Conclusao_Superior_Pct"]
    for col in colunas_obrigatorias:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória ausente na base: {col}")
    df = df.dropna(subset=colunas_obrigatorias)
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype(int)
    df["Ingressantes"] = pd.to_numeric(df["Ingressantes"], errors="coerce").fillna(0).astype(int)
    df["Concluintes"] = pd.to_numeric(df["Concluintes"], errors="coerce").fillna(0).astype(int)
    df["Taxa_Conclusao_Superior_Pct"] = pd.to_numeric(df["Taxa_Conclusao_Superior_Pct"], errors="coerce")
    return df

def calcular_estatisticas(serie):
    """Calcula todas as métricas obrigatórias da rubrica de Matemática."""
    dados = serie.dropna().to_numpy()
    if len(dados) == 0:
        return None
    
    media = np.mean(dados)
    mediana = np.median(dados)
    moda_serie = pd.Series(np.round(dados, 1)).mode()
    moda = moda_serie.iloc[0] if not moda_serie.empty else np.nan
    
    q1 = np.percentile(dados, 25)
    q2 = np.percentile(dados, 50)
    q3 = np.percentile(dados, 75)
    iqr = q3 - q1
    
    amplitude = np.max(dados) - np.min(dados)
    variancia = np.var(dados, ddof=1) if len(dados) > 1 else 0.0
    desvio_padrao = np.std(dados, ddof=1) if len(dados) > 1 else 0.0
    
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr
    outliers = dados[(dados < limite_inferior) | (dados > limite_superior)]
    
    return {
        "media": media,
        "mediana": mediana,
        "moda": moda,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "iqr": iqr,
        "min": np.min(dados),
        "max": np.max(dados),
        "amplitude": amplitude,
        "variancia": variancia,
        "desvio_padrao": desvio_padrao,
        "limite_inf": limite_inferior,
        "limite_sup": limite_superior,
        "qtd_outliers": len(outliers),
        "valores_outliers": np.round(outliers, 2).tolist()
    }

def renderizar_modulo_curso_superior():
    st.title("🎓 Indicador 2: Ensino Superior, Atração de Talentos e Mulheres em STEM")
    st.markdown("""
    **Consultoria de Dados para Governadores Estaduais:**  
    *Clientes (Personas):* **Antônio** (Gov. MG), **Ademir** (Gov. ES), **Claudinete** (Gov. SP), **Joana** (Gov. PR) e **Ana** (Gov. MS).
    """)

    st.sidebar.header("📂 Ingestão de Dados (IBGE)")
    arquivo_upload = st.sidebar.file_uploader(
        "Upload da Base IBGE (CSV ou XLSX)", 
        type=["csv", "xlsx"],
        key="upload_curso_superior",
        help="Envie a base tratada do indicador Curso Superior ou utilize os dados integrados."
    )

    if arquivo_upload is not None:
        try:
            if arquivo_upload.name.endswith(".csv"):
                df_bruto = pd.read_csv(arquivo_upload)
            else:
                df_bruto = pd.read_excel(arquivo_upload)
            st.sidebar.success("Base carregada via Upload com sucesso!")
        except Exception as e:
            st.sidebar.error(f"Erro ao ler arquivo: {e}")
            df_bruto = carregar_dados_padrao()
    else:
        df_bruto = carregar_dados_padrao()
        st.sidebar.info("Usando base oficial pré-carregada (`dados_curso_superior_ibge.csv`).")

    df = higienizar_dados(df_bruto)

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filtros Analíticos")

    ufs_disponiveis = sorted(df["UF"].unique())
    ufs_selecionadas = st.sidebar.multiselect(
        "Estado (UF):",
        options=ufs_disponiveis,
        default=ufs_disponiveis,
        key="filtro_uf_sup"
    )

    anos_min, anos_max = int(df["Ano"].min()), int(df["Ano"].max())
    intervalo_anos = st.sidebar.slider(
        "Período (Ano):",
        min_value=anos_min,
        max_value=anos_max,
        value=(anos_min, anos_max),
        key="filtro_ano_sup"
    )

    areas_disponiveis = sorted(df["Area_Conhecimento"].unique())
    areas_selecionadas = st.sidebar.multiselect(
        "Área do Conhecimento:",
        options=areas_disponiveis,
        default=areas_disponiveis,
        key="filtro_area_sup"
    )

    sexos_disponiveis = sorted(df["Sexo"].unique())
    sexos_selecionados = st.sidebar.multiselect(
        "Sexo:",
        options=sexos_disponiveis,
        default=sexos_disponiveis,
        key="filtro_sexo_sup"
    )

    df_filtrado = df[
        (df["UF"].isin(ufs_selecionadas)) &
        (df["Ano"] >= intervalo_anos[0]) &
        (df["Ano"] <= intervalo_anos[1]) &
        (df["Area_Conhecimento"].isin(areas_selecionadas)) &
        (df["Sexo"].isin(sexos_selecionados))
    ]

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para a combinação de filtros selecionada. Ajuste os filtros na barra lateral.")
        return

    stats = calcular_estatisticas(df_filtrado["Taxa_Conclusao_Superior_Pct"])

    st.subheader("📊 Painel Estatístico: Taxa de Conclusão do Ensino Superior (%)")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Média Aritmética", f"{stats['media']:.2f}%", help="Sensível a valores extremos (Outliers)")
    col2.metric("Mediana (Q2)", f"{stats['mediana']:.2f}%", delta=f"{stats['mediana'] - stats['media']:.2f}% vs Média")
    col3.metric("Moda", f"{stats['moda']:.1f}%")
    col4.metric("IQR (Q3 - Q1)", f"{stats['iqr']:.2f} p.p.", help=f"Q1: {stats['q1']:.2f}% | Q3: {stats['q3']:.2f}%")
    col5.metric("Desvio Padrão", f"{stats['desvio_padrao']:.2f} p.p.", help=f"Amplitude: {stats['amplitude']:.2f} p.p.")

    with st.expander("📐 Detalhamento Matemático: Quartis, Dispersão e Detecção de Outliers (Regra 1,5 × IQR)", expanded=True):
        c_stat1, c_stat2 = st.columns(2)
        with c_stat1:
            st.markdown(f"""
            * **1º Quartil ($Q_1 - 25\%$):** `{stats['q1']:.2f}%`
            * **2º Quartil ($Q_2 / \text{{Mediana}} - 50\%$):** `{stats['q2']:.2f}%`
            * **3º Quartil ($Q_3 - 75\%$):** `{stats['q3']:.2f}%`
            * **Intervalo Interquartil ($IQR = Q_3 - Q_1$):** `{stats['iqr']:.2f} p.p.`
            * **Amplitude Total ($Máx - Mín$):** `{stats['amplitude']:.2f} p.p.` (`{stats['min']:.2f}%` a `{stats['max']:.2f}%`)
            """)
        with c_stat2:
            st.markdown(f"""
            * **Variância ($s^2$):** `{stats['variancia']:.2f}`
            * **Desvio Padrão ($s$):** `{stats['desvio_padrao']:.2f} p.p.`
            * **Limites de Tukey ($1,5 \times IQR$):** `[ {stats['limite_inf']:.2f}%  a  {stats['limite_sup']:.2f}% ]`
            * **Outliers Detectados ({stats['qtd_outliers']} ocorrências):** `{stats['valores_outliers'] if stats['qtd_outliers'] > 0 else 'Nenhum outlier no recorte atual'}`
            """)
        st.info(
            "💡 **Leitura Analítica (Média vs. Mediana):** Quando polos de altíssima formação (como TI em São Paulo) "
            "geram outliers superiores, a **Média** é puxada para cima, criando uma falsa sensação de homogeneidade regional. "
            "Por isso, recomendamos aos governadores utilizar a **Mediana** e o **IQR** como metas de políticas públicas."
        )

    st.markdown("---")
    st.subheader("📈 Visão Executiva e Respostas às Perguntas dos Governadores")

    aba1, aba2, aba3 = st.tabs([
        "1. Evolução Histórica (Linha)", 
        "2. Mulheres em STEM vs Humanas (100% Empilhado)", 
        "3. Dispersão Territorial e Outliers (Boxplot)"
    ])

    with aba1:
        st.markdown("#### Evolução da Taxa de Graduação por Estado e Consolidado")
        df_evolucao = df_filtrado.groupby(["Ano", "UF"], as_index=False)["Taxa_Conclusao_Superior_Pct"].mean()
        df_consolidado = df_filtrado.groupby("Ano", as_index=False)["Taxa_Conclusao_Superior_Pct"].mean()
        df_consolidado["UF"] = "Média Consolidada"

        df_plot_linha = pd.concat([df_evolucao, df_consolidado], ignore_index=True)

        fig_linha = px.line(
            df_plot_linha,
            x="Ano",
            y="Taxa_Conclusao_Superior_Pct",
            color="UF",
            markers=True,
            title="Evolução Histórica da Taxa de Conclusão do Ensino Superior (%)",
            labels={"Taxa_Conclusao_Superior_Pct": "Taxa Média de Conclusão (%)", "Ano": "Ano"}
        )
        st.plotly_chart(fig_linha, use_container_width=True)

    with aba2:
        st.markdown("#### Proporção de Gênero por Área do Conhecimento e Curso (Barras 100% Empilhadas)")
        metrica_genero = st.radio(
            "Selecione o indicador de volume para comparação de gênero:",
            ["Concluintes (Diplomados)", "Ingressantes"],
            horizontal=True
        )
        col_volume = "Concluintes" if "Concluintes" in metrica_genero else "Ingressantes"

        df_genero = df_filtrado.groupby(["Area_Conhecimento", "Curso", "Sexo"], as_index=False)[col_volume].sum()
        df_genero["Total_Curso"] = df_genero.groupby(["Area_Conhecimento", "Curso"])[col_volume].transform("sum")
        df_genero["Percentual"] = (df_genero[col_volume] / df_genero["Total_Curso"]) * 100

        fig_barras = px.bar(
            df_genero,
            x="Curso",
            y="Percentual",
            color="Sexo",
            barmode="stack",
            text=df_genero["Percentual"].apply(lambda x: f"{x:.1f}%"),
            color_discrete_map={"Feminino": "#E91E63", "Masculino": "#1E88E5"},
            title=f"Proporção de {metrica_genero} por Sexo: Exatas/STEM vs. Humanas e Saúde (100% Empilhado)",
            labels={"Percentual": "Proporção (%)", "Curso": "Curso / Área"}
        )
        fig_barras.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_barras, use_container_width=True)

        st.markdown("##### Percentual Feminino por Estado: Exatas/STEM vs. Humanas")
        df_uf_sexo = df_filtrado.groupby(["UF", "Area_Conhecimento", "Sexo"], as_index=False)[col_volume].sum()
        df_uf_sexo["Total"] = df_uf_sexo.groupby(["UF", "Area_Conhecimento"])[col_volume].transform("sum")
        df_uf_sexo["Pct_Feminino"] = (df_uf_sexo[col_volume] / df_uf_sexo["Total"]) * 100
        tabela_fem = df_uf_sexo[df_uf_sexo["Sexo"] == "Feminino"].pivot(
            index="UF", columns="Area_Conhecimento", values="Pct_Feminino"
        ).round(1)
        st.dataframe(tabela_fem.style.format("{:.1f}%"), use_container_width=True)

    with aba3:
        st.markdown("#### Análise de Variação Territorial, Quartis e Outliers (Boxplot)")
        fig_box = px.box(
            df_filtrado,
            x="UF",
            y="Taxa_Conclusao_Superior_Pct",
            color="UF",
            points="all",
            hover_data=["Ano", "Curso", "Sexo"],
            title="Distribuição da Taxa de Conclusão por UF (Quartis, Mediana e Outliers)",
            labels={"Taxa_Conclusao_Superior_Pct": "Taxa de Conclusão (%)", "UF": "Estado (UF)"}
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    st.subheader("📰 Observatório de Políticas Públicas: Fuga de Cérebros e Mulheres em STEM")
    n_col1, n_col2, n_col3 = st.columns(3)

    with n_col1:
        st.image(
            "https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&w=600&q=80",
            caption="Presença feminina em laboratórios de tecnologia e engenharia."
        )
        st.markdown("#### Gap de Gênero nas Exatas")
        st.write(
            "Embora as mulheres representem quase 60% dos concluintes gerais do Ensino Superior no Brasil (IBGE/INEP), "
            "nas áreas de Computação e TICs a participação feminina entre diplomados permanece próxima de 20% a 25%."
        )

    with n_col2:
        st.image(
            "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=600&q=80",
            caption="Retenção de especialistas de alta qualificação no Sudeste e Sul."
        )
        st.markdown("#### Fuga de Cérebros e Déficit em TI")
        st.write(
            "Estados como MG, ES, PR e MS formam excelentes quadros em universidades públicas, mas sofrem com a migração "
            "de recém-formados para o eixo financeiro de São Paulo ou trabalho remoto para o exterior."
        )

    with n_col3:
        st.image(
            "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=600&q=80",
            caption="Políticas estaduais de bolsas de iniciação tecnológica."
        )
        st.markdown("#### Combate à Evasão no Ciclo Básico")
        st.write(
            "Cálculos do Censo Superior mostram que a taxa de conclusão em Exatas sofre forte queda nos primeiros 2 anos. "
            "Programas de mentoria feminina e auxílio-permanência reduzem a evasão em até 35%."
        )

if __name__ == "__main__":
    st.set_page_config(page_title="Dashboard IBGE - Curso Superior", layout="wide")
    renderizar_modulo_curso_superior()
