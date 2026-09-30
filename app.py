import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página para o modo largo (wide)
st.set_page_config(
    page_title="Port Cleanliness Planner - Gestão de Limpeza Industrial",
    page_icon="⚓",
    layout="wide"
)

# Estilização CSS personalizada
st.markdown("""
<style>
    div[data-testid="stButton"] button { font-weight: bold; }
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
    # GESTÃO DO ESTADO DA SESSÃO (GRUPOS DE PLANEJAMENTO)
    # ==========================================
    if 'lista_chefes' not in st.session_state:
        chefes_iniciais = df_os['CHEFE_TURNO'].dropna().unique().tolist() if 'CHEFE_TURNO' in df_os.columns else ["20000000 - GERSON FUENTES", "20005373 - TEMISTOCLES SANTANA"]
        st.session_state.lista_chefes = sorted(list(set(chefes_iniciais)))

    if 'plano_operacional' not in st.session_state:
        st.session_state.plano_operacional = [
            {"ID": "01", "TURMA": "AMARELA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "DIURNO", "DATA": datetime.now().strftime('%d/%m/%Y'), "HORA INICIAL": "07:00", "HORA FINAL": "08:00", "ATIVO": "3220TR04", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LAVAGEM DA MOTORIZAÇÃO DA TR + TURN-OVER DA TR", "STATUS": "Em Execução"},
            {"ID": "02", "TURMA": "BRANCA", "CHEFE DE TURNO": "20000000 - GERSON FUENTES", "TURNO": "ADM", "DATA": datetime.now().strftime('%d/%m/%Y'), "HORA INICIAL": "08:00", "HORA FINAL": "17:00", "ATIVO": "ESCAVADEIRA", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "CONTINUAR RECHEGO NA A4 + RETIRADA DE MATERIAL", "STATUS": "Em Execução"},
            {"ID": "03", "TURMA": "VERDE", "CHEFE DE TURNO": "20005373 - TEMISTOCLES SANTANA", "TURNO": "NOTURNO", "DATA": datetime.now().strftime('%d/%m/%Y'), "HORA INICIAL": "19:00", "HORA FINAL": "20:00", "ATIVO": "3220TR05", "Retirada NR12 ?": "NÃO", "DADOS DA ATIVIDADE": "LAVAGEM DA MOTORIZAÇÃO DA TR + TURN-OVER", "STATUS": "Pendente"}
        ]

    # Obter lista de todos os COD. ATIVIDADE únicos da base de dados com segurança
    col_cod_atividade = None
    for cand in ['COD. ATIVIDADE', 'COD_ATIVIDADE', 'COD ATIVIDADE', 'CODIGO ATIVIDADE']:
        if cand in df_os.columns:
            col_cod_atividade = cand
            break
    if not col_cod_atividade and len(df_os.columns) > 1:
        col_cod_atividade = df_os.columns[1] # Tentativa por índice padrão

    if col_cod_atividade and col_cod_atividade in df_os.columns:
        lista_cod_atividades = sorted(df_os[col_cod_atividade].dropna().astype(str).unique().tolist())
    else:
        lista_cod_atividades = ["001", "002", "003", "004"]

    # Obter lista de Ativos corrigida (procurando explicitamente por colunas de ativo/equipamento)
    coluna_ativo_nome = None
    for cand in ['ATIVO', 'EQUIPAMENTO', 'TAG', 'LOCAL']:
        if cand in df_os.columns:
            coluna_ativo_nome = cand
            break
    if not coluna_ativo_nome:
        # Se não achar pelo nome exato, varre as colunas procurando valores que pareçam códigos de equipamentos (ex: CT, TR)
        for col in df_os.columns:
            amostra = str(df_os[col].dropna().iloc[0]) if not df_os[col].dropna().empty else ""
            if "TR" in amostra.upper() or "CT" in amostra.upper() or "P_IER" in amostra.upper():
                coluna_ativo_nome = col
                break
        if not coluna_ativo_nome and len(df_os.columns) > 5:
            coluna_ativo_nome = df_os.columns[5]

    if coluna_ativo_nome and coluna_ativo_nome in df_os.columns:
        lista_ativos = sorted(df_os[coluna_ativo_nome].dropna().astype(str).unique().tolist())
    else:
        lista_ativos = ["CT00", "CT01", "CT02", "CT03", "CT04", "3220TR01", "3220TR02", "3230TR02", "PIER"]

    # ==========================================
    # BARRA LATERAL: MENU DE CADASTRO
    # ==========================================
    st.sidebar.header("🎛️ MENU DE PLANEJAMENTO")
    data_stamp = st.sidebar.date_input("Data do Planejamento (Stamp)", value=datetime.now().date())

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ➕ Cadastro de Chefes")
    with st.sidebar.expander("Novo Chefe de Turno"):
        novo_matricula = st.text_input("Matrícula")
        novo_nome = st.text_input("Nome Completo")
        if st.button("Salvar Chefe"):
            if novo_matricula and novo_nome:
                novo_chefe_str = f"{novo_matricula} - {novo_nome.upper()}"
                if novo_chefe_str not in st.session_state.lista_chefes:
                    st.session_state.lista_chefes.append(novo_chefe_str)
                    st.success("Chefe cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Chefe já cadastrado.")
            else:
                st.error("Preencha matrícula e nome.")

    # ==========================================
    # BLOCO DE INSERÇÃO DE ATIVIDADES (FORMULÁRIO)
    # ==========================================
    st.subheader("➕ Inserir Nova Atividade no Planejamento")
    
    with st.form("form_inserir_atividade"):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            chefe_form = st.selectbox("Chefe de Turno", options=st.session_state.lista_chefes)
            turno_form = st.selectbox("Turno", options=["DIURNO", "ADM", "NOTURNO"])
        with col_f2:
            turma_form = st.selectbox("Turma / Equipe", options=["AMARELA", "BRANCA", "VERDE", "AZUL", "ADM"])
            ativo_form = st.selectbox("Equipamento / Ativo", options=lista_ativos)
        with col_f3:
            hora_ini_form = st.text_input("Hora Inicial (HH:MM)", value="07:00")
            hora_fim_form = st.text_input("Hora Final (HH:MM)", value="08:00")

        # Lista direta de todos os COD. ATIVIDADE
        cod_atividade_escolhido = st.selectbox("Selecione o COD. ATIVIDADE", options=lista_cod_atividades)

        # Buscar descrição correspondente ao COD. ATIVIDADE
        col_desc_atividade = 'ATIVIDADE' if 'ATIVIDADE' in df_os.columns else df_os.columns[-1]
        if col_cod_atividade:
            match_desc = df_os[df_os[col_cod_atividade].astype(str) == str(cod_atividade_escolhido)]
            if not match_desc.empty:
                descricao_atividade = match_desc[col_desc_atividade].iloc[0]
            else:
                descricao_atividade = "Atividade Operacional da Base"
        else:
            descricao_atividade = "Limpeza Industrial"

        st.info(f"📌 **Descrição da Atividade Vinculada:** {descricao_atividade}")
        
        col_btn1, col_col2_btn = st.columns([1, 4])
        with col_btn1:
            botao_inserir = st.form_submit_button("🚀 Adicionar ao Plano")

        if botao_inserir:
            novo_id = f"{len(st.session_state.plano_operacional) + 1:02d}"
            novo_registro = {
                "ID": novo_id,
                "TURMA": turma_form,
                "CHEFE DE TURNO": chefe_form,
                "TURNO": turno_form,
                "DATA": data_stamp.strftime('%d/%m/%Y'),
                "HORA INICIAL": hora_ini_form,
                "HORA FINAL": hora_fim_form,
                "ATIVO": str(ativo_form).upper(),
                "Retirada NR12 ?": "NÃO",
                "DADOS DA ATIVIDADE": f"[{cod_atividade_escolhido}] {descricao_atividade}",
                "STATUS": "Agendado"
            }
            st.session_state.plano_operacional.append(novo_registro)
            st.success("Atividade adicionada com sucesso à grade!")
            st.rerun()

    st.divider()

    # ==========================================
    # GRADES DE PLANEJAMENTO DIÁRIO (DIURNO, ADM, NOTURNO)
    # ==========================================
    st.subheader("📋 Grade de Planejamento Diário Operacional")
    st.markdown(f"**Data do Plano (Stamp Ativo):** {data_stamp.strftime('%d/%m/%Y')}")

    df_plano_atual = pd.DataFrame(st.session_state.plano_operacional)

    turnos_secoes = [
        ("DIURNO", "☀️️ Turno Diurno"),
        ("ADM", "🏢 Turno Administrativo (ADM)"),
        ("NOTURNO", "🌙 Turno Noturno")
    ]

    for codigo_turno, titulo_turno in turnos_secoes:
        st.markdown(f"### {titulo_turno}")
        df_turno_atual = df_plano_atual[df_plano_atual['TURNO'] == codigo_turno]
        
        if not df_turno_atual.empty:
            st.dataframe(df_turno_atual, use_container_width=True)
        else:
            st.info(f"Nenhuma atividade programada para o {titulo_turno.lower()}. Utilize o formulário acima para adicionar.")

    st.divider()

    # ==========================================
    # SEÇÃO DE VISUALIZAÇÃO DOS DADOS BRUTOS DA BASE
    # ==========================================
    st.subheader("📑 Base de Ordens de Serviço Processadas (Referência)")
    st.dataframe(df_os.head(50), use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar o sistema: {e}")
