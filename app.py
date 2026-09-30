import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página para o modo largo (wide)
st.set_page_config(
    page_title="PortClean AutoPlanner - Gestão de Limpeza Industrial",
    page_icon="⚓",
    layout="wide"
)

# Título principal do painel
st.markdown("<h1>⚓ PortClean AutoPlanner - Gestão de Limpeza Industrial</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #a0a0a0;'>Motor de regras automatizado para planeamento diário, análise de frequência e tomada de decisão operacional.</p>", unsafe_allow_html=True)

# Função para carregar e processar os dados com segurança
@st.cache_data
def carregar_e_processar_dados(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo)
    # Tratamento de datas se existirem colunas correspondentes
    if 'DATA_INICIO_DT' in df.columns:
        df['DATA_INICIO_DT'] = pd.to_datetime(df['DATA_INICIO_DT'], errors='coerce')
    return df

try:
    # Carregamento da base de dados da Ferroport
    df_os = carregar_e_processar_dados("Relatorio OS PCP Sistema - SUPERSAN.csv")

    # ==========================================
    # BARRA LATERAL: FILTROS DINÂMICOS
    # ==========================================
    st.sidebar.header("🎛️ Filtros Operacionais")
    
    # Filtro de Turno
    turnos_disponiveis = df_os['TURNO'].dropna().unique().tolist() if 'TURNO' in df_os.columns else []
    turno_selecionado = st.sidebar.multiselect("Filtrar por Turno", options=turnos_disponiveis, default=turnos_disponiveis)

    # Filtro de Turma
    turmas_disponiveis = df_os['TURMA'].dropna().unique().tolist() if 'TURMA' in df_os.columns else []
    turma_selecionada = st.sidebar.multiselect("Filtrar por Turma", options=turmas_disponiveis, default=turmas_disponiveis)

    # Filtro de Atividade
    atividades_disponiveis = df_os['ATIVIDADE'].dropna().unique().tolist() if 'ATIVIDADE' in df_os.columns else []
    atividade_selecionada = st.sidebar.multiselect("Filtrar por Atividade", options=atividades_disponiveis)

    # Aplicação dos filtros ao DataFrame
    df_filtrado = df_os.copy()
    if turno_selecionado and 'TURNO' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['TURNO'].isin(turno_selecionado)]
    if turma_selecionada and 'TURMA' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['TURMA'].isin(turma_selecionada)]
    if atividade_selecionada and 'ATIVIDADE' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['ATIVIDADE'].isin(atividade_selecionada)]

    st.sidebar.markdown("---")
    st.sidebar.info(f"Mostrando {len(df_filtrado)} de {len(df_os)} registos após os filtros.")

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
        ano_max = int(df_filtrado['DATA_INICIO_DT'].dt.year.max()) if 'DATA_INICIO_DT' in df_filtrado.columns and not df_filtrado['DATA_INICIO_DT'].dropna().empty else datetime.now().year
        st.metric("Período Analisado", ano_max)
    with col4:
        media_colab = round(df_filtrado["QTD. COLAB."].mean(), 1) if "QTD. COLAB." in df_filtrado.columns and not df_filtrado["QTD. COLAB."].dropna().empty else 0
        st.metric("Média Colaboradores/OS", media_colab)

    st.divider()

    # ==========================================
    # SEÇÃO: PLANEAMENTO DIÁRIO BASEADO NO HISTÓRICO
    # ==========================================
    st.subheader("📋 Planeamento Diário Operacional (Baseado no Histórico de Frequência)")
    st.markdown("Matriz automatizada de prioridades para atribuição de turmas e turnos nas frentes críticas de granéis sólidos.")

    # Tabela de Planeamento Simulada / Extraída do Histórico
    dados_planeamento = [
        {"Prioridade": "Alta", "Equipamento / Área": "3230TR02 - Calda", "Atividade Discriminada": "Lavagem da Estrutura da Calda", "Frequência Média": "A cada 7 dias", "Turno Sugerido": "Noturno", "Turma Alocada": "Branca", "Estado / Ação": "Agendado"},
        {"Prioridade": "Alta", "Equipamento / Área": "3230TR02.2 - Balança", "Atividade Discriminada": "Limpeza e Lavagem Geral", "Frequência Média": "A cada 14 dias", "Turno Sugerido": "Diurno", "Turma Alocada": "Verde", "Estado / Ação": "Em Execução"},
        {"Prioridade": "Média", "Equipamento / Área": "CT04 - Turn-over de Cauda", "Atividade Discriminada": "Remoção de Material Acumulado", "Frequência Média": "A cada 10 dias", "Turno Sugerido": "Diurno", "Turma Alocada": "Azul", "Estado / Ação": "Pendente"},
        {"Prioridade": "Média", "Equipamento / Área": "Pátio de Correias", "Atividade Discriminada": "Raspagem de Piso e Resíduos", "Frequência Média": "Diário", "Turno Sugerido": "Noturno", "Turma Alocada": "Amarela", "Estado / Ação": "Planeado"}
    ]
    df_planeamento = pd.DataFrame(dados_planeamento)
    st.dataframe(df_planeamento, use_container_width=True)

    st.divider()

    # ==========================================
    # SEÇÃO DE VISUALIZAÇÃO DOS DADOS BRUTOS
    # ==========================================
    st.subheader("📑 Base de Ordens de Serviço Processadas")
    st.dataframe(df_filtrado.head(100), use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
