import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página para o modo largo (wide)
st.set_page_config(
    page_title="Port Cleanliness Planner - Gestão de Limpeza Industrial",
    page_icon="⚓",
    layout="wide"
)

# Estilização CSS personalizada para os botões coloridos na barra lateral
st.markdown("""
<style>
    div[data-testid="stButton"] button[key*="btn_turma_AMARELA"] { background-color: #ffc107 !important; color: #000 !important; font-weight: bold; }
    div[data-testid="stButton"] button[key*="btn_turma_AZUL"] { background-color: #007bff !important; color: #fff !important; font-weight: bold; }
    div[data-testid="stButton"] button[key*="btn_turma_BRANCA"] { background-color: #e0e0e0 !important; color: #000 !important; font-weight: bold; }
    div[data-testid="stButton"] button[key*="btn_turma_VERDE"] { background-color: #28a745 !important; color: #fff !important; font-weight: bold; }
    div[data-testid="stButton"] button[key*="btn_turma_ADM"] { background-color: #6c757d !important; color: #fff !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Título principal atualizado
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
    # BARRA LATERAL: FILTROS POR BOTÕES
    # ==========================================
    st.sidebar.header("🎛️ Filtros Operacionais")
    
    # --- FILTRO POR TURNO (BOTÕES) ---
    st.sidebar.markdown("### 🕒 Filtrar por Turno")
    turnos_disponiveis = [str(t).upper() for t in df_os['TURNO'].dropna().unique().tolist()] if 'TURNO' in df_os.columns else ["DIURNO", "NOTURNO"]
    turnos_disponiveis = sorted(list(set(turnos_disponiveis)))

    if 'turnos_ativos' not in st.session_state:
        st.session_state.turnos_ativos = {turno: True for turno in turnos_disponiveis}

    turno_selecionado_filtros = []
    col_turno1, col_turno2 = st.sidebar.columns(2)
    
    for i, turno in enumerate(turnos_disponiveis):
        ativo = st.session_state.turnos_ativos.get(turno, True)
        label = f"🟢 {turno}" if ativo else f"⚪ {turno} (Off)"
        coluna_atual = col_turno1 if i % 2 == 0 else col_turno2
        
        with coluna_atual:
            if st.button(label, key=f"btn_turno_{turno}", use_container_width=True):
                st.session_state.turnos_ativos[turno] = not st.session_state.turnos_ativos[turno]
                st.rerun()
                
        if st.session_state.turnos_ativos.get(turno, True):
            turno_selecionado_filtros.append(turno)

    # --- FILTRO POR TURMA (BOTÕES COLORIDOS EM DUAS COLUNAS + ADM ABAIXO) ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏷️ Filtro por Turma")
    
    turmas_principais = ["AMARELA", "AZUL", "BRANCA", "VERDE"]

    if 'turmas_ativas' not in st.session_state:
        st.session_state.turmas_ativas = {turma: True for turma in turmas_principais + ["ADM"]}

    turma_selecionada_filtros = []
    col_t1, col_t2 = st.sidebar.columns(2)

    for i, turma in enumerate(turmas_principais):
        ativo = st.session_state.turmas_ativas.get(turma, True)
        label = f"{turma}" if ativo else f"{turma} (Off)"
        coluna_atual = col_t1 if i % 2 == 0 else col_t2
        
        with coluna_atual:
            if st.button(label, key=f"btn_turma_{turma}", use_container_width=True):
                st.session_state.turmas_ativas[turma] = not st.session_state.turmas_ativas[turma]
                st.rerun()
                
        if st.session_state.turmas_ativas.get(turma, True):
            turma_selecionada_filtros.append(turma)

    # Botão ADM centralizado abaixo
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    adm_ativo = st.session_state.turmas_ativas.get("ADM", True)
    adm_label = "ADM" if adm_ativo else "ADM (Off)"
    
    col_esq, col_centro, col_dir = st.sidebar.columns([1, 2, 1])
    with col_centro:
        if st.button(adm_label, key="btn_turma_ADM", use_container_width=True):
            st.session_state.turmas_ativas["ADM"] = not st.session_state.turmas_ativas["ADM"]
            st.rerun()
            
    if st.session_state.turmas_ativas.get("ADM", True):
        turma_selecionada_filtros.append("ADM")

    # Filtro de Atividade
    st.sidebar.markdown("---")
    atividades_disponiveis = df_os['ATIVIDADE'].dropna().unique().tolist() if 'ATIVIDADE' in df_os.columns else []
    atividade_selecionada = st.sidebar.multiselect("Filtrar por Atividade", options=atividades_disponiveis)

    # Aplicação dos filtros ao DataFrame
    df_filtrado = df_os.copy()
    if turno_selecionado_filtros and 'TURNO' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['TURNO'].astype(str).str.upper().isin(turno_selecionado_filtros)]
    if turma_selecionada_filtros and 'TURMA' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['TURMA'].astype(str).str.upper().isin(turma_selecionada_filtros)]
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
    # SEÇÃO: PLANEJAMENTO DIÁRIO COM LAYOUT FEROPORT
    # ==========================================
    st.subheader("📋 Planejamento Diário Operacional")
    st.markdown("Matriz automatizada alinhada ao modelo operacional com status de execução.")

    dados_planeamento = [
        {"ID": "01", "TURMA": "AMARELA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "DIURNO", "DATA": "22/09/2026", "HORA": "07-08", "ATIVO": "3220TR04", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LAVAGEM DA MOTORIZAÇÃO DA TR + TURN-OVER DA TR", "Estado / Ação": "Agendado"},
        {"ID": "02", "TURMA": "BRANCA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "DIURNO", "DATA": "22/09/2026", "HORA": "07-09", "ATIVO": "3230TR02", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LAVAGEM GERAL DA ESTRUTURA INFERIOR DA TR ATÉ A CT5", "Estado / Ação": "Em Execução"},
        {"ID": "03", "TURMA": "BRANCA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "DIURNO", "DATA": "22/09/2026", "HORA": "09-10", "ATIVO": "CT00", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LIMPEZA DO PISO INFERIOR + CANALETA DESAGUADORA", "Estado / Ação": "Pendente"},
        {"ID": "04", "TURMA": "BRANCA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "DIURNO", "DATA": "22/09/2026", "HORA": "10-11", "ATIVO": "CT01", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LIMPEZA DO PISO INFERIOR + CANALETA DESAGUADORA", "Estado / Ação": "Planeado"},
        {"ID": "05", "TURMA": "VERDE", "CHEFE DE TURNO": "20005373 - TEMISTOCLES SANTANA", "TURNO": "NOTURNO", "DATA": "22/09/2026", "HORA": "19-20", "ATIVO": "3220TR05", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LAVAGEM DA MOTORIZAÇÃO DA TR + TURN-OVER", "Estado / Ação": "Agendado"},
        {"ID": "06", "TURMA": "VERDE", "CHEFE DE TURNO": "20005373 - TEMISTOCLES SANTANA", "TURNO": "NOTURNO", "DATA": "22/09/2026", "HORA": "20-21", "ATIVO": "CT01", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LIMPEZA DO PISO INFERIOR DA CT + CANALETA DESAGUADORA", "Estado / Ação": "Em Execução"}
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
