# Projeto Integrador Etapa 3 — Números que Falam: Descobrindo o Brasil (IBGE)

## Indicador 2: Curso Superior (Atração de Talentos e Mulheres em STEM)

### Personas Atendidas
- **Antônio** (Governador de Minas Gerais)
- **Ademir** (Governador do Espírito Santo)
- **Claudinete** (Governadora de São Paulo)
- **Joana** (Governadora do Paraná)
- **Ana** (Governadora do Mato Grosso do Sul)

---

### Estrutura do Repositório
- `modulo_curso_superior.py`: Módulo individual completo em Streamlit com ingestão (`st.file_uploader`), pipeline ETL, cálculo de métricas estatísticas (Média, Mediana, Moda, Quartis Q1/Q2/Q3, IQR, Amplitude, Variância, Desvio Padrão e Outliers via regra 1,5xIQR), gráficos interativos (Linha, Barras 100% Empilhadas e Boxplot) e observatório de notícias.
- `gerar_base_curso_superior.py`: Script gerador da base higienizada do indicador.
- `dados_curso_superior_ibge.csv`: Base de dados limpa em formato CSV pronta para ingestão.
- `dados_curso_superior_ibge.xlsx`: Planilha Excel formatada com a base tratada e aba de resumo estatístico por UF.
- `app.py`: Arquivo principal com menu lateral pronto para unificar os 5 módulos do grupo.
- `requirements.txt`: Lista de bibliotecas necessárias para rodar o projeto.

---

### Como Executar Localmente
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
