import streamlit as st
import pandas as pd
from datetime import datetime, time

# Configuração da página para o modo largo (wide)
st.set_page_config(
    page_title="Port Cleanliness Planner - Gestão de Limpeza Industrial",
    page_icon="⚓",
    layout="wide"
)

# Título principal do painel
st.markdown("<h1>⚓ Port Cleanliness Planner - Gestão de Limpeza Industrial</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #a0a0a0;'>Motor de regras automatizado para planejamento diário, análise de frequência e tomada de decisão operacional.</p>", unsafe_allow_html=True)

# Função para carregar e processar os dados com segurança e deteção de delimitador
@st.cache_data
def carregar_e_processar_dados(caminho_arquivo):
    try:
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8', low_memory=False)
        if len(df.columns) <= 1:
            df = pd.read_csv(caminho_arquivo, sep=',', encoding='utf-8', low_memory=False)
    except:
        df = pd.read_csv(caminho_arquivo, sep=None, engine='python', encoding='utf-8')
        
    if 'DATA_INICIO_DT' in df.columns:
        df['DATA_INICIO_DT'] = pd.to_datetime(df['DATA_INICIO_DT'], errors='coerce')
    return df

try:
    df_os = carregar_e_processar_dados("Relatorio OS PCP Sistema - SUPERSAN.csv")

    # ==========================================
    # BARRA LATERAL: PARÂMETROS E FILTROS EM LISTAS SUSPENSAS
    # ==========================================
    st.sidebar.header("🎛️ Parâmetros do Planejamento")
    
    # Stamp de Data (Calendário)
    data_stamp = st.sidebar.date_input("Data do Planejamento (Stamp)", value=datetime.now().date())

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Filtros de Parâmetros")

    # Lista suspensa para Chefe de Turno
    chefes_disponiveis = df_os['CHEFE_TURNO'].dropna().unique().tolist() if 'CHEFE_TURNO' in df_os.columns else ["20000000 - GERSON FUENTES", "20005373 - TEMISTOCLES SANTANA"]
    chefe_selecionado = st.sidebar.selectbox("Chefe de Turno", options=["TODOS"] + chefes_disponiveis)

    # Lista suspensa para Turno
    turnos_disponiveis = df_os['TURNO'].dropna().unique().tolist() if 'TURNO' in df_os.columns else ["DIURNO", "NOTURNO", "ADM"]
    turno_selecionado = st.sidebar.selectbox("Turno", options=["TODOS"] + turnos_disponiveis)

    # Lista suspensa para Turma
    turmas_disponiveis = df_os['TURMA'].dropna().unique().tolist() if 'TURMA' in df_os.columns else ["AMARELA", "BRANCA", "VERDE", "AZUL", "ADM"]
    turma_selecionada = st.sidebar.selectbox("Turma", options=["TODOS"] + turmas_disponiveis)

    # Aplicação dos parâmetros de filtros ao DataFrame base
    df_filtrado = df_os.copy()
    if chefe_selecionado != "TODOS" and 'CHEFE_TURNO' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['CHEFE_TURNO'] == chefe_selecionado]
    if turno_selecionado != "TODOS" and 'TURNO' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['TURNO'] == turno_selecionado]
    if turma_selecionada != "TODOS" and 'TURMA' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['TURMA'] == turma_selecionada]

    st.sidebar.markdown("---")
    st.sidebar.info(f"Mostrando {len(df_filtrado)} registos com base nos parâmetros selecionados.")

    # ==========================================
    # MÉTRICAS PRINCIPAIS EM CARDS
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Ordens de Serviço", len(df_filtrado))
    with col2:
        num_atividades = df_filtrado["COD. ATIVIDADE"].nunique() if "COD. ATIVIDADE" in df_filtrado.columns else 0
        st.metric("Atividades Únicas Mapeadas", num_atividades)
    with col3:
        st.metric("Data Stamp Ativa", data_stamp.strftime('%d/%m/%Y'))
    with col4:
        media_colab = round(df_filtrado["QTD. COLAB."].mean(), 1) if "QTD. COLAB." in df_filtrado.columns and not df_filtrado["QTD. COLAB."].dropna().empty else 0
        st.metric("Média Colaboradores/OS", media_colab)

    st.divider()

    # ==========================================
    # CONSTRUÇÃO DINÂMICA DO PLANEJAMENTO DIÁRIO
    # ==========================================
    st.subheader("📋 Planejamento Diário Operacional Dinâmico")
    st.markdown(f"**Data do Plano (Stamp):** {data_stamp.strftime('%d/%m/%Y')} | Matriz gerada a partir dos parâmetros operacionais.")

    # Base pré-programada que responde aos seletores da barra lateral
    dados_base_planejamento = [
        {"ID": "01", "TURMA": "AMARELA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "DIURNO", "DATA": data_stamp.strftime('%d/%m/%Y'), "HORA INICIAL": "07:00", "HORA FINAL": "08:00", "ATIVO": "3220TR04", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LAVAGEM DA MOTORIZAÇÃO DA TR + TURN-OVER DA TR", "STATUS": "Em Execução"},
        {"ID": "02", "TURMA": "BRANCA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "DIURNO", "DATA": data_stamp.strftime('%d/%m/%Y'), "HORA INICIAL": "08:00", "HORA FINAL": "09:00", "ATIVO": "3230TR02", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LAVAGEM GERAL DA ESTRUTURA INFERIOR DA TR ATÉ A CT5", "STATUS": "Agendado"},
        {"ID": "03", "TURMA": "AMARELA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "ADM", "DATA": data_stamp.strftime('%d/%m/%Y'), "HORA INICIAL": "08:00", "HORA FINAL": "17:00", "ATIVO": "ESCAVADEIRA HIDRAULICA", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "CONTINUAR RECHEGO NA A4 + RETIRADA DE MATERIAL", "STATUS": "Em Execução"},
        {"ID": "04", "TURMA": "VERDE", "CHEFE DE TURNO": "20005373 - TEMISTOCLES SANTANA", "TURNO": "NOTURNO", "DATA": data_stamp.strftime('%d/%m/%Y'), "HORA INICIAL": "19:00", "HORA FINAL": "20:00", "ATIVO": "3220TR05", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LAVAGEM DA MOTORIZAÇÃO DA TR + TURN-OVER", "STATUS": "Pendente"}
    ]

    df_plano = pd.DataFrame(dados_base_planejamento)

    # Filtrar dinamicamente a tabela de planejamento com base nos seletores laterais
    if chefe_selecionado != "TODOS":
        df_plano = df_plano[df_plano['CHEFE DE TURNO'] == chefe_selecionado]
    if turno_selecionado != "TODOS":
        df_plano = df_plano[df_plano['TURNO'] == turno_selecionado]
    if turma_selecionada != "TODOS":
        df_plano = df_plano[df_plano['TURMA'] == turma_selecionada]

    # Exibição dividida por secções de Turno para clareza operacional
    for t_sec in ["DIURNO", "ADM", "NOTURNO"]:
        df_sec = df_plano[df_plano['TURNO'] == t_sec]
        if not df_sec.empty:
            icones_sec = {"DIURNO": "☀️ Diurno", "ADM": "🏢 Administrativo (ADM)", "NOTURNO": "🌙 Noturno"}
            st.markdown(f"### {icones_sec.get(t_sec, t_sec)}")
            st.dataframe(df_sec, use_container_width=True)

    st.divider()

    # ==========================================
    # SEÇÃO DE VISUALIZAÇÃO DOS DADOS BRUTOS
    # ==========================================
    st.subheader("📑 Base de Ordens de Serviço Processadas")
    st.dataframe(df_filtrado.head(100), use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
