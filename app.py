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
    div[data-testid="stButton"] button[key*="btn_turma_AMARELA"] { background-color: #ffc107 !important; color: #000 !important; font-weight: bold; border: 1px solid #e0a800; }
    div[data-testid="stButton"] button[key*="btn_turma_AZUL"] { background-color: #007bff !important; color: #fff !important; font-weight: bold; border: 1px solid #0056b3; }
    div[data-testid="stButton"] button[key*="btn_turma_BRANCA"] { background-color: #f8f9fa !important; color: #212529 !important; font-weight: bold; border: 1px solid #dae0e5; }
    div[data-testid="stButton"] button[key*="btn_turma_VERDE"] { background-color: #28a745 !important; color: #fff !important; font-weight: bold; border: 1px solid #1e7e34; }
    div[data-testid="stButton"] button[key*="btn_turma_ADM"] { background-color: #6c757d !important; color: #fff !important; font-weight: bold; border: 1px solid #545b62; }
</style>
""", unsafe_allow_html=True)

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
    # BARRA LATERAL: MENU DE PLANEJAMENTO
    # ==========================================
    st.sidebar.header("🎛️ MENU DE PLANEJAMENTO")
    
    # Stamp de Data (Calendário)
    data_stamp = st.sidebar.date_input("Data do Planejamento (Stamp)", value=datetime.now().date())

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Filtros de Parâmetros")

    # Inicializar lista de chefes no session_state se não existir
    if 'lista_chefes' not in st.session_state:
        chefes_iniciais = df_os['CHEFE_TURNO'].dropna().unique().tolist() if 'CHEFE_TURNO' in df_os.columns else ["20000000 - GERSON FUENTES", "20005373 - TEMISTOCLES SANTANA"]
        st.session_state.lista_chefes = sorted(list(set(chefes_iniciais)))

    # Seleção de Chefe de Turno
    chefe_selecionado = st.sidebar.selectbox("Chefe de Turno", options=["TODOS"] + st.session_state.lista_chefes)

    # --- PROCEDIMENTO DE CADASTRO DE NOVO CHEFE DE TURNO ---
    with st.sidebar.expander("➕ Cadastrar Novo Chefe de Turno"):
        novo_matricula = st.text_input("Matrícula")
        novo_nome = st.text_input("Nome Completo")
        if st.button("Salvar Novo Chefe"):
            if novo_matricula and novo_nome:
                novo_chefe_str = f"{novo_matricula} - {novo_nome.upper()}"
                if novo_chefe_str not in st.session_state.lista_chefes:
                    st.session_state.lista_chefes.append(novo_chefe_str)
                    st.success(f"Chefe {novo_chefe_str} cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Este chefe já está cadastrado.")
            else:
                st.error("Preencha a Matrícula e o Nome.")

    # Lista suspensa para Turno
    turnos_disponiveis = df_os['TURNO'].dropna().unique().tolist() if 'TURNO' in df_os.columns else ["DIURNO", "NOTURNO", "ADM"]
    turno_selecionado = st.sidebar.selectbox("Turno", options=["TODOS"] + sorted([str(t) for t in turnos_disponiveis]))

    # Lista suspensa para Turma
    turmas_disponiveis = df_os['TURMA'].dropna().unique().tolist() if 'TURMA' in df_os.columns else ["AMARELA", "BRANCA", "VERDE", "AZUL", "ADM"]
    turma_selecionada = st.sidebar.selectbox("Turma", options=["TODOS"] + sorted([str(t) for t in turmas_disponiveis]))

    # --- MENU DE ATIVIDADES (EXTRAÍDO DA BASE SEM DUPLICATAS) ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Seleção de Atividades")
    
    # Extrair atividades da base, limpando duplicatas
    if 'ATIVIDADE' in df_os.columns:
        atividades_unicas = sorted(df_os['ATIVIDADE'].dropna().astype(str).unique().tolist())
    else:
        atividades_unicas = ["LAVAGEM DA MOTORIZAÇÃO DA TR", "LIMPEZA DO PISO INFERIOR", "RETIRADA DE MATERIAL"]
        
    atividade_selecionada_menu = st.sidebar.selectbox("Buscar Atividade Planejada", options=["TODAS"] + atividades_unicas)

    # Aplicação dos parâmetros de filtros ao DataFrame base
    df_filtrado = df_os.copy()
    if chefe_selecionado != "TODOS" and 'CHEFE_TURNO' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['CHEFE_TURNO'] == chefe_selecionado]
    if turno_selecionado != "TODOS" and 'TURNO' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['TURNO'] == turno_selecionado]
    if turma_selecionada != "TODOS" and 'TURMA' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['TURMA'] == turma_selecionada]
    if atividade_selecionada_menu != "TODAS" and 'ATIVIDADE' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['ATIVIDADE'] == atividade_selecionada_menu]

    st.sidebar.markdown("---")
    st.sidebar.info(f"Mostrando {len(df_filtrado)} registos com base nos filtros.")

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
    st.subheader("📋 Planejamento Diário Operacional")
    st.markdown(f"**Data do Plano (Stamp):** {data_stamp.strftime('%d/%m/%Y')} | Matriz dinâmica baseada nos parâmetros operacionais.")

    # Base pré-programada que responde aos seletores
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
    if atividade_selecionada_menu != "TODAS":
        df_plano = df_plano[df_plano['DADOS DA ATIVIDADE'].str.contains(atividade_selecionada_menu, case=False, na=False)]

    # Exibição dividida pelas 3 seções exigidas
    for t_sec in ["DIURNO", "ADM", "NOTURNO"]:
        df_sec = df_plano[df_plano['TURNO'] == t_sec]
        if not df_sec.empty:
            icones_sec = {"DIURNO": "☀️ Turno Diurno", "ADM": "🏢 Turno Administrativo (ADM)", "NOTURNO": "🌙 Turno Noturno"}
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
