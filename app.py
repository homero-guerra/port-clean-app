import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página para o modo largo (wide)
st.set_page_config(
    page_title="Port Cleanliness Planner - Gestão de Limpeza Industrial",
    page_icon="⚓",
    layout="wide"
)

# Estilização CSS avançada para eliminar margens e subir tudo ao máximo no topo
st.markdown("""
<style>
    /* Remover espaçamento superior da barra lateral */
    [data-testid="stSidebar"] {
        min-width: 420px !important;
        max-width: 460px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
    }
    
    /* Remover o espaçamento superior padrão da página principal */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }
    
    div[data-testid="stButton"] button { font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Título principal do painel alinhado no topo absoluto
st.markdown("<h1>⚓ Port Cleanliness Planner - Gestão de Limpeza Industrial</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #a0a0a0; margin-top: -10px;'>Motor de regras automatizado para planejamento diário, análise de frequência e tomada de decisão operacional.</p>", unsafe_allow_html=True)

# Função para carregar e processar os dados com segurança e deteção de delimitador
@st.cache_data
def carregar_e_processar_dados(caminho_arquivo):
    try:
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8', low_memory=False)
        if len(df.columns) <= 1:
            df = pd.read_csv(caminho_arquivo, sep=',', encoding='utf-8', low_memory=False)
    except:
        df = pd.read_csv(caminho_arquivo, sep=None, engine='python', encoding='utf-8')
        
    df.columns = df.columns.str.strip()
        
    if 'DATA_INICIO_DT' in df.columns:
        df['DATA_INICIO_DT'] = pd.to_datetime(df['DATA_INICIO_DT'], errors='coerce')
    return df

try:
    df_os = carregar_e_processar_dados("Relatorio OS PCP Sistema - SUPERSAN.csv")

    # ==========================================
    # GESTÃO DO ESTADO DA SESSÃO
    # ==========================================
    if 'lista_chefes' not in st.session_state:
        chefes_iniciais = df_os['CHEFE_TURNO'].dropna().unique().tolist() if 'CHEFE_TURNO' in df_os.columns else ["20000000 - GERSON FUENTES", "20005373 - TEMISTOCLES SANTANA"]
        st.session_state.lista_chefes = sorted(list(set(chefes_iniciais)))

    if 'plano_operacional' not in st.session_state:
        st.session_state.plano_operacional = [
            {"ID": "01", "TURMA": "AMARELA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "DIURNO", "DATA": datetime.now().strftime('%d/%m/%Y'), "HORA INICIAL": "07:00", "HORA FINAL": "08:00", "ATIVO": "3220TR04", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "[3220TR04.3] LAVAGEM DA MOTORIZAÇÃO DA TR", "STATUS": "Em Execução"},
            {"ID": "02", "TURMA": "BRANCA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "ADM", "DATA": datetime.now().strftime('%d/%m/%Y'), "HORA INICIAL": "08:00", "HORA FINAL": "17:00", "ATIVO": "CT08", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "[CT08.4] CONTINUAR RECHEGO NA A4", "STATUS": "Em Execução"},
            {"ID": "03", "TURMA": "VERDE", "CHEFE DE TURNO": "20005373 - TEMISTOCLES SANTANA", "TURNO": "NOTURNO", "DATA": datetime.now().strftime('%d/%m/%Y'), "HORA INICIAL": "19:00", "HORA FINAL": "20:00", "ATIVO": "3220TR05", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "[3220TR05.4] LAVAGEM DA MOTORIZAÇÃO", "STATUS": "Pendente"}
        ]

    # Identificar colunas exatas na base
    col_cod = 'COD. ATIVIDADE' if 'COD. ATIVIDADE' in df_os.columns else 'COD_ATIVIDADE'
    col_desc = 'ATIVIDADE' if 'ATIVIDADE' in df_os.columns else df_os.columns[-1]
    col_ativo = 'ATIVO' if 'ATIVO' in df_os.columns else (df_os.columns[6] if len(df_os.columns) > 6 else df_os.columns[0])

    # Criar lista única e consolidada (sem duplicações) combinando Código + Descrição
    if col_cod in df_os.columns and col_desc in df_os.columns:
        df_unicos = df_os[[col_cod, col_desc]].dropna().drop_duplicates(subset=[col_cod])
        lista_opcoes_atividades = sorted([f"{row[col_cod]} - {row[col_desc]}" for _, row in df_unicos.iterrows()])
    else:
        lista_opcoes_atividades = ["3230TR02.1 - LAVAGEM DA ESTRUTURA DA CALDA DA 3230TR02", "CT08.4 - CONTINUAR RECHEGO NA A4"]

    # ==========================================
    # BARRA LATERAL: MENU DE PLANEJAMENTO E INSERÇÃO
    # ==========================================
    st.sidebar.markdown("### 🎛️ MENU DE PLANEJAMENTO")
    data_stamp = st.sidebar.date_input("Data do Planejamento (Stamp)", value=datetime.now().date())

    with st.sidebar:
        if st.button("🚀 Adicionar ao Plano", use_container_width=True):
            st.session_state['trigger_adicionar'] = True

    st.sidebar.markdown("---")

    with st.sidebar.form("form_inserir_atividade"):
        
        col_lbl_chefe, col_btn_plus = st.columns([4, 1])
        with col_lbl_chefe:
            chefe_form = st.selectbox("Chefe de Turno", options=st.session_state.lista_chefes)
        with col_btn_plus:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            abrir_cadastro = st.form_submit_button("➕")

        if abrir_cadastro:
            st.session_state['mostrar_cadastro_chefe'] = not st.session_state.get('mostrar_cadastro_chefe', False)

        if st.session_state.get('mostrar_cadastro_chefe', False):
            st.markdown("---")
            st.markdown("#### 👤 Registar Novo Chefe")
            novo_matricula = st.text_input("Matrícula")
            novo_nome = st.text_input("Nome Completo")
            if st.form_submit_button("💾 Salvar Novo Chefe"):
                if novo_matricula and novo_nome:
                    novo_chefe_str = f"{novo_matricula} - {novo_nome.upper()}"
                    if novo_chefe_str not in st.session_state.lista_chefes:
                        st.session_state.lista_chefes.append(novo_chefe_str)
                        st.session_state['mostrar_cadastro_chefe'] = False
                        st.success("Chefe registado com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Este chefe já está registado.")
                else:
                    st.error("Preencha matrícula e nome.")
            st.markdown("---")

        turma_form = st.selectbox("Turma / Equipe", options=["AMARELA", "BRANCA", "VERDE", "AZUL", "ADM"])
        turno_form = st.selectbox("Turno", options=["DIURNO", "ADM", "NOTURNO"])
        
        c_h1, c_h2 = st.columns(2)
        with c_h1:
            hora_ini_form = st.text_input("Hora Inicial (HH:MM)", value="07:00")
        with c_h2:
            hora_fim_form = st.text_input("Hora Final (HH:MM)", value="08:00")

        st.markdown("---")
        
        opcao_selecionada = st.selectbox("Selecione o COD. ATIVIDADE", options=lista_opcoes_atividades)

        if " - " in opcao_selecionada:
            cod_atividade_escolhido, descricao_atividade = opcao_selecionada.split(" - ", 1)
        else:
            cod_atividade_escolhido = opcao_selecionada
            descricao_atividade = "Atividade Operacional Registrada"

        if col_cod in df_os.columns and col_ativo in df_os.columns:
            resultado_sql = df_os[df_os[col_cod].astype(str) == str(cod_atividade_escolhido)]
            if not resultado_sql.empty:
                ativo_extraido = str(resultado_sql[col_ativo].iloc[0]).upper()
            else:
                ativo_extraido = "GERAL"
        else:
            ativo_extraido = "GERAL"

        st.info(f"{descricao_atividade}")

        botao_inserir_form = st.form_submit_button("🚀 Salvar na Grade", use_container_width=True)

        if botao_inserir_form or st.session_state.pop('trigger_adicionar', False):
            novo_id = f"{len(st.session_state.plano_operacional) + 1:02d}"
            novo_registro = {
                "ID": novo_id,
                "TURMA": turma_form,
                "CHEFE DE TURNO": chefe_form,
                "TURNO": turno_form,
                "DATA": data_stamp.strftime('%d/%m/%Y'),
                "HORA INICIAL": hora_ini_form,
                "HORA FINAL": hora_fim_form,
                "ATIVO": ativo_extraido,
                "Retirada NR12 ?": "NÃO",
                "DADOS DA ATIVIDADE": f"[{cod_atividade_escolhido}] {descricao_atividade}",
                "STATUS": "Agendado"
            }
            st.session_state.plano_operacional.append(novo_registro)
            st.success(f"Adicionado ao Turno {turno_form}!")
            st.rerun()

    # ==========================================
    # ÁREA PRINCIPAL: GRADES DE PLANEJAMENTO OPERACIONAL
    # ==========================================
    st.markdown("### 📋 Grade de Planejamento Diário Operacional")
    st.markdown(f"<p style='color: #a0a0a0; margin-top: -8px;'>Data Stamp Ativa: {data_stamp.strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)

    df_plano_atual = pd.DataFrame(st.session_state.plano_operacional)

    turnos_secoes = [
        ("DIURNO", "☀️ Turno Diurno"),
        ("ADM", "🏢 Turno Administrativo (ADM)"),
        ("NOTURNO", "🌙 Turno Noturno")
    ]

    for codigo_turno, titulo_turno in turnos_secoes:
        st.markdown(f"#### {titulo_turno}")
        df_turno_atual = df_plano_atual[df_plano_atual['TURNO'] == codigo_turno]
        
        if not df_turno_atual.empty:
            st.dataframe(df_turno_atual, use_container_width=True)
        else:
            st.info(f"Nenhuma atividade no {titulo_turno.lower()}.")

    st.divider()

    # ==========================================
    # SEÇÃO DE VISUALIZAÇÃO DOS DADOS BRUTOS DA BASE
    # ==========================================
    st.subheader("📑 Base de Ordens de Serviço Processadas (Referência)")
    st.dataframe(df_os.head(50), use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar o sistema: {e}")
