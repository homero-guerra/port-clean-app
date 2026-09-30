import pandas as pd
import streamlit as st

# Configuração da Página do Aplicativo
st.set_page_config(
    page_title="PortClean AutoPlanner - Ferroport", layout="wide"
)

st.title("⚓ PortClean AutoPlanner - Gestão de Limpeza Industrial")
st.markdown(
    "Motor de regras automatizado para planejamento diário e análise de frequência."
)


@st.cache_data
def carregar_e_processar_dados(caminho_arquivo):
  # Leitura do arquivo CSV de ordens de serviço
  df = pd.read_csv(caminho_arquivo, sep=None, engine="python")
  df["DATA_INICIO_DT"] = pd.to_datetime(
      df["DATA INICIO"], format="%d-%m-%Y", errors="coerce"
  )
  df = df.sort_values(by=["COD. ATIVIDADE", "DATA_INICIO_DT"])

  # Cálculo do intervalo em dias entre execuções consecutivas
  df["DIFF_DAYS"] = (
      df.groupby("COD. ATIVIDADE")["DATA_INICIO_DT"].diff().dt.days
  )
  return df


# Carregamento da base de dados
try:
  df_os = carregar_e_processar_dados("Relatorio OS PCP Sistema - SUPERSAN.csv")

  # Métricas Principais no Topo
  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric("Total de Ordens de Serviço", len(df_os))
  with col2:
    st.metric(
        "Atividades Únicas Mapeadas", df_os["COD. ATIVIDADE"].nunique()
    )
  with col3:
    st.metric("Período Analisado", f"{df_os['DATA_INICIO_DT'].dt.year.max()}")

  st.divider()

  # Seção de Visualização dos Dados
  st.subheader("📋 Base de Ordens de Serviço Processadas")
  st.dataframe(df_os.head(100), use_container_width=True)

except Exception as e:
  st.error(f"Erro ao carregar os dados: {e}")