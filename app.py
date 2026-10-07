import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import urllib.parse
import base64

# Configuração da página (título limpo e sem ícone)
st.set_page_config(
    page_title="Plano de Limpeza",
    layout="wide"
)

# Mapa de cores oficial das equipes/turmas
mapa_cores = {
    "AMARELA": "#FFD700",
    "BRANCA": "#F5F5F5",
    "VERDE": "#32CD32",
    "AZUL": "#1E90FF",
    "ADM": "#A9A9A9"
}

# Estilização CSS para máxima compactação e organização da barra lateral
st.markdown("""
<style>
    /* Puxar elementos para cima na barra lateral */
    [data-testid="stSidebar"] {
        min-width: 400px !important;
        max-width: 440px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 0.1rem !important;
        padding-bottom: 1rem !important;
    }
    [data-testid="stSidebar"] .element-container {
        margin-bottom: -0.5rem !important;
    }
    
    /* Compactar espaços verticais gerais da página principal */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1rem !important;
    }
    h1 {
        margin-bottom: 0.1rem !important;
    }
    
    /* Padronizar botões gerais */
    div[data-testid="stButton"] button {
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Título principal atualizado
st.markdown("<h1>Plano de Limpeza Operacional</h1>", unsafe_allow_html=True)

# Função para carregar e processar os dados com segurança e detecção de delimitador
@st.cache_data
def carregar_e_processar_dados(caminho_arquivo):
    try:
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8', low_memory=False)
        if len(df.columns) <= 1:
            df = pd.read_csv(caminho_arquivo, sep=',', encoding='utf-8', low_memory=False)
    except:
        df = pd.read_csv(caminho_arquivo, sep=None, engine='python', encoding='utf-8')
        
    df.columns = df.columns.str.strip()
        
    # Converter colunas de data candidatas a Data Final para datetime
    colunas_data_final = ['DATA_FINAL_DT', 'DATA_FINAL', 'DT_FINAL', 'DATA FINAL']
    for c_dt in colunas_data_final:
        if c_dt in df.columns:
            df[c_dt] = pd.to_datetime(df[c_dt], errors='coerce')
            
    return df

try:
    df_os = carregar_e_processar_dados("Relatorio OS PCP Sistema - SUPERSAN.csv")
except Exception as e:
    df_os = pd.DataFrame()

# ==========================================
# PERSISTÊNCIA EM NUVEM (FICHEIROS DE DADOS E CONFIGURAÇÕES)
# ==========================================
ARQUIVO_BANCO_DADOS = "plano_operacional_nuvem.csv"
ARQUIVO_CONFIG_EMAILS = "config_emails_nuvem.txt"
ARQUIVO_CONFIG_CHEFES = "config_chefes_nuvem.txt"

def carregar_plano_nuvem():
    if os.path.exists(ARQUIVO_BANCO_DADOS):
        try:
            df_persisted = pd.read_csv(ARQUIVO_BANCO_DADOS, encoding='utf-8')
            if 'UID' not in df_persisted.columns:
                df_persisted['UID'] = [f"UID_{i}_{int(datetime.now().timestamp())}" for i in range(len(df_persisted))]
            
            if 'Observação' in df_persisted.columns:
                df_persisted['Observação'] = df_persisted['Observação'].fillna("").astype(str)
            else:
                df_persisted['Observação'] = ""
                
            if 'Ativo' in df_persisted.columns:
                df_persisted['Ativo'] = df_persisted['Ativo'].apply(
                    lambda x: "GERAL" if str(x).upper() in ["DIURNO", "NOTURNO", "ADM", "NAN", "NONE", ""] else x
                )
            return df_persisted.to_dict(orient='records')
        except:
            pass
    return [
        {
            "UID": "UID_1_001",
            "TURMA": "AMARELA", 
            "CHEFE DE TURNO": "20000000 - GERSON FUENTES", 
            "TURNO": "DIURNO", 
            "DATA": datetime.now().strftime('%d/%m/%Y'), 
            "Cód. Atividade": "3220TR04.3",
            "Hora Inicial": "07:00", 
            "Hora Final": "08:00", 
            "Ativo": "3220TR04", 
            "Retirada NR12": "NÃO", 
            "Dados da Atividade": "LAVAGEM DA MOTORIZAÇÃO DA TR",
            "Observação": ""
        },
        {
            "UID": "UID_2_002",
            "TURMA": "BRANCA", 
            "CHEFE DE TURNO": "20000000 - GERSON FUENTES", 
            "TURNO": "ADM", 
            "DATA": datetime.now().strftime('%d/%m/%Y'), 
            "Cód. Atividade": "CT08.4",
            "Hora Inicial": "08:00", 
            "Hora Final": "17:00", 
            "Ativo": "CT08", 
            "Retirada NR12": "NÃO", 
            "Dados da Atividade": "CONTINUAR RECHEGO NA A4",
            "Observação": ""
        }
    ]

def salvar_plano_nuvem(lista_registros):
    try:
        df_to_save = pd.DataFrame(lista_registros)
        if 'Observação' in df_to_save.columns:
            df_to_save['Observação'] = df_to_save['Observação'].fillna("").astype(str)
        df_to_save.to_csv(ARQUIVO_BANCO_DADOS, index=False, encoding='utf-8')
    except Exception:
        pass

def carregar_emails_nuvem():
    if os.path.exists(ARQUIVO_CONFIG_EMAILS):
        try:
            with open(ARQUIVO_CONFIG_EMAILS, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if conteudo:
                    return conteudo
        except:
            pass
    return "operacao.limpeza@ferroport.com.br, supervisao.pcp@ferroport.com.br, gerencia.operacional@ferroport.com.br"

def salvar_emails_nuvem(emails_str):
    try:
        with open(ARQUIVO_CONFIG_EMAILS, "w", encoding="utf-8") as f:
            f.write(emails_str)
    except:
        pass

def carregar_chefes_nuvem():
    chefes_iniciais = df_os['CHEFE_TURNO'].dropna().unique().tolist() if not df_os.empty and 'CHEFE_TURNO' in df_os.columns else ["20000000 - GERSON FUENTES", "20005373 - TEMISTOCLES SANTANA"]
    if os.path.exists(ARQUIVO_CONFIG_CHEFES):
        try:
            with open(ARQUIVO_CONFIG_CHEFES, "r", encoding="utf-8") as f:
                linhas = [line.strip() for line in f if line.strip()]
                if linhas:
                    chefes_iniciais.extend(linhas)
        except:
            pass
    return sorted(list(set(chefes_iniciais)))

def salvar_chefe_nuvem(novo_chefe):
    try:
        chefes_atuais = []
        if os.path.exists(ARQUIVO_CONFIG_CHEFES):
            with open(ARQUIVO_CONFIG_CHEFES, "r", encoding="utf-8") as f:
                chefes_atuais = [line.strip() for line in f if line.strip()]
        if novo_chefe not in chefes_atuais:
            chefes_atuais.append(novo_chefe)
            with open(ARQUIVO_CONFIG_CHEFES, "w", encoding="utf-8") as f:
                f.write("\n".join(chefes_atuais))
    except:
        pass

def remover_chefe_nuvem(chefe_para_remover):
    try:
        if os.path.exists(ARQUIVO_CONFIG_CHEFES):
            with open(ARQUIVO_CONFIG_CHEFES, "r", encoding="utf-8") as f:
                chefes_atuais = [line.strip() for line in f if line.strip()]
            if chefe_para_remover in chefes_atuais:
                chefes_atuais.remove(chefe_para_remover)
                with open(ARQUIVO_CONFIG_CHEFES, "w", encoding="utf-8") as f:
                    f.write("\n".join(chefes_atuais))
    except:
        pass

try:
    # ==========================================
    # GESTÃO DO ESTADO DA SESSÃO
    # ==========================================
    if 'lista_chefes' not in st.session_state:
        st.session_state.lista_chefes = carregar_chefes_nuvem()

    if 'plano_operacional' not in st.session_state:
        st.session_state.plano_operacional = carregar_plano_nuvem()

    if 'emails_distribuicao' not in st.session_state:
        st.session_state.emails_distribuicao = carregar_emails_nuvem()

    col_cod = 'COD. ATIVIDADE' if not df_os.empty and 'COD. ATIVIDADE' in df_os.columns else 'COD_ATIVIDADE'
    col_desc = 'ATIVIDADE' if not df_os.empty and 'ATIVIDADE' in df_os.columns else (df_os.columns[-1] if not df_os.empty else 'DESCRICAO')
    col_ativo = 'ATIVO' if not df_os.empty and 'ATIVO' in df_os.columns else (df_os.columns[6] if not df_os.empty and len(df_os.columns) > 6 else 'ATIVO')

    if not df_os.empty and col_cod in df_os.columns and col_desc in df_os.columns:
        df_unicos = df_os[[col_cod, col_desc]].dropna().drop_duplicates(subset=[col_cod])
        lista_opcoes_atividades = sorted([f"{row[col_cod]} - {row[col_desc]}" for _, row in df_unicos.iterrows()])
    else:
        lista_opcoes_atividades = ["3230TR02.1 - LAVAGEM DA ESTRUTURA DA CALDA DA 3230TR02", "CT08.4 - CONTINUAR RECHEGO NA A4"]

    # Lista de horários de 1 em 1 hora
    lista_horarios = [f"{h:02d}:00" for h in range(24)]

    # ==========================================
    # BARRA LATERAL: MENU DE PLANEJAMENTO REATIVO
    # ==========================================
    st.sidebar.markdown("### 🎛️ MENU DE PLANEJAMENTO")

    # Linha 1: Data, Hora Inicial e Hora Final alinhados lado a lado
    col_d, col_h1, col_h2 = st.sidebar.columns([1.2, 1.0, 1.0])
    with col_d:
        data_stamp = st.sidebar.date_input("Data", value=datetime.now().date())
    with col_h1:
        hora_ini_form = st.sidebar.selectbox("Hora Inicial", options=lista_horarios, index=7, key="sel_h_ini")
    with col_h2:
        hora_fim_form = st.sidebar.selectbox("Hora Final", options=lista_horarios, index=8, key="sel_h_fim")
        
    # Linha 2: Turma / Equipe e Turno alinhados lado a lado
    col_turma, col_turno = st.sidebar.columns([1, 1])
    with col_turma:
        turma_form = st.sidebar.selectbox("Turma / Equipe", options=["AMARELA", "BRANCA", "VERDE", "AZUL", "ADM"], key="sel_turma_main")
    with col_turno:
        turno_form = st.sidebar.selectbox("Turno", options=["DIURNO", "ADM", "NOTURNO"], key="sel_turno_main")

    # Linha 3: Chefe de Turno reduzido com o botão de gestão (⚙️) alinhado ao lado
    col_chefe_sel, col_btn_gear = st.sidebar.columns([2.3, 0.7])
    with col_chefe_sel:
        chefe_form = st.sidebar.selectbox("Chefe de Turno", options=st.session_state.lista_chefes, key="sel_chefe_main")
    with col_btn_gear:
        st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)
        if st.sidebar.button("⚙️", key="btn_cad_chefe", help="Gerenciar Chefes"):
            st.session_state['mostrar_gestao_chefe'] = not st.session_state.get('mostrar_gestao_chefe', False)

    # Painel retrátil de Gestão de Chefes (Cadastro e Exclusão)
    if st.session_state.get('mostrar_gestao_chefe', False):
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### 👥 Gestão de Chefes")
        novo_matricula = st.sidebar.text_input("Matrícula")
        novo_nome = st.sidebar.text_input("Nome Completo")
        col_s_ch, col_r_ch = st.sidebar.columns(2)
        with col_s_ch:
            if st.sidebar.button("💾 Salvar", key="save_chefe_btn", use_container_width=True):
                if novo_matricula and novo_nome:
                    novo_chefe_str = f"{novo_matricula} - {novo_nome.upper()}"
                    if novo_chefe_str not in st.session_state.lista_chefes:
                        st.session_state.lista_chefes.append(novo_chefe_str)
                        salvar_chefe_nuvem(novo_chefe_str)
                        st.session_state['mostrar_gestao_chefe'] = False
                        st.sidebar.success("Salvo com sucesso!")
                        st.rerun()
                    else:
                        st.sidebar.warning("Já cadastrado.")
                else:
                    st.sidebar.error("Preencha os campos.")
        with col_r_ch:
            chefe_a_remover = st.sidebar.selectbox("Remover", options=st.session_state.lista_chefes, key="sel_rem_chefe_clean", label_visibility="collapsed")
            if st.sidebar.button("🗑️ Excluir", key="conf_rem_chefe_btn", use_container_width=True):
                chefes_base_original = df_os['CHEFE_TURNO'].dropna().unique().tolist() if not df_os.empty and 'CHEFE_TURNO' in df_os.columns else []
                if chefe_a_remover in chefes_base_original:
                    st.sidebar.warning("Impossível remover chefe da base oficial.")
                else:
                    if chefe_a_remover in st.session_state.lista_chefes:
                        st.session_state.lista_chefes.remove(chefe_a_remover)
                        remover_chefe_nuvem(chefe_a_remover)
                        st.session_state['mostrar_gestao_chefe'] = False
                        st.sidebar.success("Removido!")
                        st.rerun()
        st.sidebar.markdown("---")

    cor_dinamica = mapa_cores.get(turma_form, "#FFD700")
    css_dinamico = f"""
    <style>
        div[data-baseweb="select"] span[title="AMARELA"],
        div[data-baseweb="select"] span[title="BRANCA"],
        div[data-baseweb="select"] span[title="VERDE"],
        div[data-baseweb="select"] span[title="AZUL"],
        div[data-baseweb="select"] span[title="ADM"],
        div[data-baseweb="select"] span[title="DIURNO"],
        div[data-baseweb="select"] span[title="NOTURNO"] {{
            color: {cor_dinamica} !important;
            font-weight: bold !important;
        }}
    </style>
    """
    st.sidebar.markdown(css_dinamico, unsafe_allow_html=True)

    st.sidebar.markdown("---")
    
    # Campo reativo para atualizar o aviso textual instantaneamente
    opcao_selecionada = st.sidebar.selectbox(
        "Selecione o COD. ATIVIDADE", 
        options=lista_opcoes_atividades,
        index=0,
        placeholder="Digite para pesquisar...",
        key="sel_atividade_main"
    )

    if " - " in opcao_selecionada:
        cod_atividade_escolhido, descricao_atividade = opcao_selecionada.split(" - ", 1)
    else:
        cod_atividade_escolhido = opcao_selecionada
        descricao_atividade = "Atividade Operacional Registrada"

    # Campo Observação logo abaixo do aviso textual
    observacao_form = st.sidebar.text_input("Observação", key="obs_form_main")

    ativo_extraido = "GERAL"
    if not df_os.empty and col_cod in df_os.columns and col_ativo in df_os.columns:
        resultado_sql = df_os[df_os[col_cod].astype(str) == str(cod_atividade_escolhido)]
        if not resultado_sql.empty:
            val_ativo = str(resultado_sql[col_ativo].iloc[0]).upper()
            if val_ativo not in ["DIURNO", "NOTURNO", "ADM", "NAN", "NONE", ""]:
                ativo_extraido = val_ativo
            else:
                partes = cod_atividade_escolhido.split('.')
                if len(partes) > 0 and len(partes[0]) >= 4:
                    ativo_extraido = partes[0][:8]
    else:
        partes = cod_atividade_escolhido.split('.')
        if len(partes) > 0:
            ativo_extraido = partes[0][:8]

    if ativo_extraido in ["DIURNO", "NOTURNO", "ADM"]:
        partes = cod_atividade_escolhido.split('.')
        ativo_extraido = partes[0][:8] if len(partes) > 0 else "GERAL"

    # Aviso textual atualizado instantaneamente em tempo real
    st.sidebar.info(f"{descricao_atividade}")

    if st.sidebar.button("💾 Incluir na Grade", use_container_width=True, type="primary"):
        novo_uid = f"UID_{int(datetime.now().timestamp())}_{len(st.session_state.plano_operacional)}"
        novo_registro = {
            "UID": novo_uid,
            "TURMA": turma_form,
            "CHEFE DE TURNO": chefe_form,
            "TURNO": turno_form,
            "DATA": data_stamp.strftime('%d/%m/%Y'),
            "Cód. Atividade": cod_atividade_escolhido,
            "Hora Inicial": hora_ini_form,
            "Hora Final": hora_fim_form,
            "Ativo": ativo_extraido,
            "Retirada NR12": "NÃO",
            "Dados da Atividade": descricao_atividade,
            "Observação": str(observacao_form) if observacao_form else ""
        }
        st.session_state.plano_operacional.append(novo_registro)
        salvar_plano_nuvem(st.session_state.plano_operacional)
        st.sidebar.success(f"Adicionado e salvo com sucesso no Turno {turno_form}!")
        st.rerun()

    # ==========================================
    # ÁREA PRINCIPAL: TÍTULO, CALENDÁRIO PROPORCIONAL E BOTÃO DE IMPRESSÃO
    # ==========================================
    df_plano_atual = pd.DataFrame(st.session_state.plano_operacional)
    
    if not df_plano_atual.empty and 'Ativo' in df_plano_atual.columns:
        df_plano_atual['Ativo'] = df_plano_atual['Ativo'].apply(
            lambda x: "GERAL" if str(x).upper() in ["DIURNO", "NOTURNO", "ADM", "NAN", "NONE", ""] else x
        )
    if not df_plano_atual.empty:
        if 'Observação' not in df_plano_atual.columns:
            df_plano_atual['Observação'] = ""
        else:
            df_plano_atual['Observação'] = df_plano_atual['Observação'].fillna("").astype(str)

    col_tit_grade, col_filtro_grade, col_vazio_medio, col_down_grade = st.columns([3.2, 1.6, 2.2, 1.0])
    with col_tit_grade:
        st.markdown("### 📋 Grade de Planejamento Diário")
    with col_filtro_grade:
        data_pesquisa_obj = st.date_input("🔍 Consultar Plano por Data", value=datetime.now().date(), label_visibility="collapsed")
        data_selecionada_filtro = data_pesquisa_obj.strftime('%d/%m/%Y')

    df_filtrado_data = df_plano_atual[df_plano_atual['DATA'] == data_selecionada_filtro] if not df_plano_atual.empty else pd.DataFrame()

    data_hoje_str = datetime.now().strftime('%d/%m/%Y')
    modo_leitura = (data_selecionada_filtro != data_hoje_str)

    if modo_leitura:
        st.info(f"🔒 **Modo Leitura Ativado** para a data {data_selecionada_filtro}. Os registos de datas anteriores ficam em consulta protegida.")

    # Consulta na base oficial do GitHub (SUPERSAN.csv) utilizando estritamente a coluna Data Final
    col_dt_final = None
    if not df_os.empty:
        for c_cand in ['DATA_FINAL_DT', 'DATA_FINAL', 'DT_FINAL', 'DATA FINAL']:
            if c_cand in df_os.columns:
                col_dt_final = c_cand
                break

    if col_dt_final and not df_os.empty:
        df_os_filtrado = df_os[df_os[col_dt_final].dt.date == data_pesquisa_obj]
        if not df_os_filtrado.empty:
            with st.expander(f"📂 Ver Registros da Base SUPERSAN (Filtrado por Data Final: {data_selecionada_filtro}) — {len(df_os_filtrado)} ordens", expanded=False):
                st.dataframe(df_os_filtrado, use_container_width=True, hide_index=True)

    # Extrair metadados específicos para cada Turno individualmente
    df_diurno_ref = df_filtrado_data[df_filtrado_data['TURNO'].astype(str).str.strip().str.upper() == "DIURNO"] if not df_filtrado_data.empty else pd.DataFrame()
    if not df_diurno_ref.empty:
        turma_diurno = str(df_diurno_ref.iloc[-1].get('TURMA', 'AMARELA')).strip().upper()
        chefe_diurno = str(df_diurno_ref.iloc[-1].get('CHEFE_TURNO', df_diurno_ref.iloc[-1].get('CHEFE DE TURNO', 'N/D')))
    else:
        turma_diurno = "AMARELA"
        chefe_diurno = "20000000 - GERSON FUENTES"

    df_adm_ref = df_filtrado_data[df_filtrado_data['TURNO'].astype(str).str.strip().str.upper() == "ADM"] if not df_filtrado_data.empty else pd.DataFrame()
    if not df_adm_ref.empty:
        turma_adm = str(df_adm_ref.iloc[-1].get('TURMA', 'ADM')).strip().upper()
        chefe_adm = str(df_adm_ref.iloc[-1].get('CHEFE_TURNO', df_adm_ref.iloc[-1].get('CHEFE DE TURNO', 'N/D')))
    else:
        turma_adm = "ADM"
        chefe_adm = "20000000 - GERSON FUENTES"

    df_noturno_ref = df_filtrado_data[df_filtrado_data['TURNO'].astype(str).str.strip().str.upper() == "NOTURNO"] if not df_filtrado_data.empty else pd.DataFrame()
    if not df_noturno_ref.empty:
        turma_noturno = str(df_noturno_ref.iloc[-1].get('TURMA', 'AMARELA')).strip().upper()
        chefe_noturno = str(df_noturno_ref.iloc[-1].get('CHEFE_TURNO', df_noturno_ref.iloc[-1].get('CHEFE DE TURNO', 'N/D')))
    else:
        turma_noturno = "AMARELA"
        chefe_noturno = "20000000 - GERSON FUENTES"

    data_comum = data_selecionada_filtro

    # ==========================================
    # FUNÇÃO HTML DE IMPRESSÃO (PAISAGEM COM CONTROLE DE ADM E VERSO NOTURNO)
    # ==========================================
    def gerar_html_paisagem(df_dados, data_plano):
        tem_adm = not df_dados[df_dados['TURNO'].astype(str).str.strip().str.upper() == "ADM"].empty

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Plano de Limpeza Operacional - {data_plano}</title>
    <style>
        @page {{ size: landscape; margin: 6mm; }}
        body {{ font-family: Arial, sans-serif; color: #0f172a; margin: 0; padding: 5px; }}
        .header {{ border-bottom: 2px solid #003366; padding-bottom: 4mm; margin-bottom: 10px; }}
        .header h1 {{ margin: 0; font-size: 16px; color: #003366; }}
        .header p {{ margin: 2px 0 0 0; color: #475569; font-size: 10px; }}
        .bloco-container {{ margin-top: 10px; }}
        .page-break {{ page-break-before: always; }}
        .bloco-titulo {{ 
            background-color: #f1f5f9; 
            padding: 5px 8px; 
            font-size: 11px; 
            font-weight: bold; 
            color: #003366; 
            border-left: 4px solid #003366; 
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 3px; font-size: 9px; }}
        th {{ background-color: #003366; color: white; padding: 4px; text-align: left; }}
        td {{ padding: 3px; border: 1px solid #cbd5e1; }}
        tr:nth-child(even) {{ background-color: #f8fafc; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>FERROPORT — PLANO DE LIMPEZA OPERACIONAL</h1>
        <p>Relatório Consolidado Diário &nbsp;|&nbsp; <b>Data do Plano:</b> {data_plano}</p>
    </div>"""
        
        if df_dados.empty:
            html += "<p>Nenhuma atividade registada para esta data.</p>"
        else:
            turnos_html = [
                ("DIURNO", "Turno Diurno", turma_diurno, chefe_diurno),
                ("ADM", "Turno ADM", turma_adm, chefe_adm),
                ("NOTURNO", "Turno Noturno", turma_noturno, chefe_noturno)
            ]
            
            primeiro_bloco = True
            for codigo_turno, titulo_turno, t_info, c_info in turnos_html:
                df_t = df_dados[df_dados['TURNO'].astype(str).str.strip().str.upper() == codigo_turno]
                
                if not df_t.empty:
                    if codigo_turno == "NOTURNO" and tem_adm:
                        html += '<div class="page-break"></div>'

                    html += f"""
                    <div class="bloco-container">
                        <div class="bloco-titulo">
                            <span>{titulo_turno}</span>
                            <span style="font-size: 10px; font-weight: normal; color: #334155;">
                                👥 <b>Equipa:</b> {t_info} &nbsp;|&nbsp; 👤 <b>Chefe:</b> {c_info} &nbsp;|&nbsp; 📅 <b>Data:</b> {data_plano}
                            </span>
                        </div>
                        <table>
                            <thead>
                                <tr><th>Nº</th><th>Cód. Atividade</th><th>Hora Ini.</th><th>Hora Fim.</th><th>Ativo</th><th>NR12</th><th>Dados da Atividade</th><th>Observação</th></tr>
                            </thead>
                            <tbody>
                    """
                    for idx, (_, row) in enumerate(df_t.iterrows(), 1):
                        html += f"<tr><td>{idx}</td><td>{row.get('Cód. Atividade', '')}</td><td>{row.get('Hora Inicial', '')}</td><td>{row.get('Hora Final', '')}</td><td>{row.get('Ativo', '')}</td><td>{row.get('Retirada NR12', '')}</td><td>{row.get('Dados da Atividade', '')}</td><td>{row.get('Observação', '')}</td></tr>"
                    html += "</tbody></table></div>"
                    primeiro_bloco = False
                    
        html += """
            <script>
                window.onload = function() { 
                    window.print(); 
                }
            </script>
        </body>
        </html>
        """
        return html

    with col_down_grade:
        if not df_filtrado_data.empty:
            timestamp_str = datetime.now().strftime("%d%m%H%M")
            nome_arquivo_download = f"Plano_de_Limpeza_{timestamp_str}.html"
            
            html_para_download = gerar_html_paisagem(df_filtrado_data, data_selecionada_filtro)
            b64_down = base64.b64encode(html_para_download.encode('utf-8')).decode()
            
            st.markdown(
                f"""
                <a href="data:text/html;base64,{b64_down}" download="{nome_arquivo_download}" target="_blank" style="text-decoration: none;">
                    <button style="width: 100%; background-color: #003366; color: white; border: none; padding: 9px 12px; border-radius: 4px; font-weight: bold; font-size: 14px; cursor: pointer; font-family: sans-serif;">
                        🖨️ Imprimir
                    </button>
                </a>
                """,
                unsafe_allow_html=True
            )
        else:
            st.button("🖨️ Imprimir", disabled=True, use_container_width=True)

    st.markdown("""
    <style>
        button[kind="primary"] {
            background-color: #003366 !important;
            border-color: #003366 !important;
            color: white !important;
        }
        button[kind="primary"]:hover {
            background-color: #002244 !important;
            border-color: #002244 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # CAMPO: LISTA DE DISTRIBUIÇÃO PERSISTIDA EM NUVEM COM CALLBACK (ALINHADO E COMPACTO)
    # ==========================================
    col_lbl_dist, col_input_email, col_btn_email = st.columns([1.2, 5.8, 1.0])
    with col_lbl_dist:
        st.markdown("<div style='padding-top: 6px; font-weight: 600; font-size: 14px;'>Lista de Distribuição:</div>", unsafe_allow_html=True)
    with col_input_email:
        def atualizar_emails_callback():
            novo_valor = st.session_state.input_emails_state
            salvar_emails_nuvem(novo_valor)
            st.session_state.emails_distribuicao = novo_valor

        lista_emails = st.text_input(
            "Destinatários", 
            value=st.session_state.emails_distribuicao, 
            key="input_emails_state",
            on_change=atualizar_emails_callback,
            label_visibility="collapsed"
        )
    with col_btn_email:
        btn_enviar_outlook = st.button("✉️ Enviar Plano", use_container_width=True)

    if btn_enviar_outlook:
        salvar_emails_nuvem(lista_emails)
        st.session_state.emails_distribuicao = lista_emails
        
        assunto = f"[Ferroport] Plano de Limpeza Operacional - {data_selecionada_filtro}"
        corpo = f"""Prezados(as),

Segue em anexo o Plano de Limpeza para o dia {data_selecionada_filtro}.

Atenciosamente,"""
        
        assunto_encoded = urllib.parse.quote(assunto)
        corpo_encoded = urllib.parse.quote(corpo)
        mailto_link = f"mailto:{lista_emails}?subject={assunto_encoded}&body={corpo_encoded}"
        
        st.markdown(f'<meta http-equiv="refresh" content="0;url={mailto_link}">', unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # MODAL DE ALTERAÇÃO DE HORÁRIO
    # ==========================================
    @st.dialog("🕒 Alterar Horário da Atividade")
    def modal_alterar_horario(uid_alvo, titulo_t):
        st.write(f"Editando horário no **{titulo_t}**")
        nova_h_ini = st.selectbox("Nova Hora Inicial", options=lista_horarios, key="modal_nova_hi")
        nova_h_fim = st.selectbox("Nova Hora Final", options=lista_horarios, key="modal_nova_hf")
        
        if st.button("💾 Gravar Alteração", type="primary", use_container_width=True):
            for reg in st.session_state.plano_operacional:
                if str(reg.get('UID')) == str(uid_alvo):
                    reg['Hora Inicial'] = nova_h_ini
                    reg['Hora Final'] = nova_h_fim
                    break
            salvar_plano_nuvem(st.session_state.plano_operacional)
            st.success("Horário alterado com sucesso!")
            st.rerun()

    turnos_secoes = [
        ("DIURNO", "☀️ Turno Diurno"),
        ("ADM", "🏢 Turno ADM"),
        ("NOTURNO", "🌙 Turno Noturno")
    ]

    for codigo_turno, titulo_turno in turnos_secoes:
        df_turno_atual = df_filtrado_data[df_filtrado_data['TURNO'].astype(str).str.strip().str.upper() == codigo_turno] if not df_filtrado_data.empty else pd.DataFrame()
        
        if codigo_turno == "ADM":
            turma_info = turma_adm
            chefe_info = chefe_adm
            data_info = data_comum
            cor_destaque = mapa_cores.get(turma_adm, "#A9A9A9")
        elif codigo_turno == "DIURNO":
            turma_info = turma_diurno
            chefe_info = chefe_diurno
            data_info = data_comum
            cor_destaque = mapa_cores.get(turma_diurno, "#FFD700")
        else:
            turma_info = turma_noturno
            chefe_info = chefe_noturno
            data_info = data_comum
            cor_destaque = mapa_cores.get(turma_noturno, "#1E90FF")

        selecao_key = f"dataframe_grid_{codigo_turno}_{data_selecionada_filtro}"
        
        # Cabeçalho do Bloco
        col_titulo_bloco, col_vazio_bloco = st.columns([6.5, 1.5])
        with col_titulo_bloco:
            html_cabecalho = f"""
            <div style="display: flex; align-items: baseline; gap: 15px; flex-wrap: wrap;">
                <h4 style="color: {cor_destaque}; margin: 0; padding: 0;">{titulo_turno}</h4>
                <span style="color: #d0d0d0; font-size: 14px;">
                    <span style="color: {cor_destaque};">👥</span> <b>Equipa:</b> <span style="color:{cor_destaque}; font-weight:bold;">{turma_info}</span> 
                    &nbsp;|&nbsp; <span style="color: {cor_destaque};">👤</span> <b>Chefe:</b> <span style="color:{cor_destaque};">{chefe_info}</span> 
                    &nbsp;|&nbsp; 📅 <b>Data:</b> <span style="color:{cor_destaque};">{data_info}</span>
                </span>
            </div>
            """
            st.markdown(html_cabecalho, unsafe_allow_html=True)
        
        # Preparação do DataFrame com coluna de checkbox para seleção na tabela editável
        if not df_turno_atual.empty:
            df_exibicao = df_turno_atual.copy()
            if 'UID' not in df_exibicao.columns:
                df_exibicao['UID'] = [f"UID_{i}" for i in range(len(df_exibicao))]
            if 'Observação' not in df_exibicao.columns:
                df_exibicao['Observação'] = ""
            else:
                df_exibicao['Observação'] = df_exibicao['Observação'].fillna("").astype(str)
                
            df_exibicao.insert(0, 'Selecionar', False)
            df_exibicao.insert(1, 'Nº', range(1, len(df_exibicao) + 1))
            
            colunas_exibir = ['Selecionar', 'Nº', 'UID', 'Cód. Atividade', 'Hora Inicial', 'Hora Final', 'Ativo', 'Retirada NR12', 'Dados da Atividade', 'Observação']
            df_final_exibir = df_exibicao[[c for c in colunas_exibir if c in df_exibicao.columns]]
            
            edited_df = st.data_editor(
                df_final_exibir,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Selecionar": st.column_config.CheckboxColumn("Sel.", width="small", default=False),
                    "Nº": st.column_config.NumberColumn("Nº", width="small", disabled=True),
                    "Cód. Atividade": st.column_config.TextColumn("Cód. Atividade", width="medium", disabled=True),
                    "Hora Inicial": st.column_config.TextColumn("Hora Ini.", width="small", disabled=True),
                    "Hora Final": st.column_config.TextColumn("Hora Fim.", width="small", disabled=True),
                    "Ativo": st.column_config.TextColumn("Ativo", width="small", disabled=True),
                    "Retirada NR12": st.column_config.TextColumn("NR12", width="small", disabled=True),
                    "Dados da Atividade": st.column_config.TextColumn("Dados da Atividade", width="large", disabled=True),
                    "Observação": st.column_config.TextColumn("Observação", width="medium", disabled=False if not modo_leitura else True),
                    "UID": None
                },
                key=selecao_key
            )
            
            # Sincronizar alterações de Observação
            if not modo_leitura and 'Observação' in edited_df.columns:
                changed = False
                for _, row in edited_df.iterrows():
                    uid_val = row.get('UID')
                    obs_val = str(row.get('Observação', ''))
                    for reg in st.session_state.plano_operacional:
                        if str(reg.get('UID')) == str(uid_val):
                            if str(reg.get('Observação', '')) != obs_val:
                                reg['Observação'] = obs_val
                                changed = True
                if changed:
                    salvar_plano_nuvem(st.session_state.plano_operacional)
            
            # Identificar linhas selecionadas pelas caixas de seleção
            linhas_selecionadas_idx = edited_df.index[edited_df['Selecionar'] == True].tolist()
        else:
            linhas_selecionadas_idx = []

        # Botões de ação (Alterar Horário e Excluir) colocados logo ABAIXO da tabela
        col_vazio_btns, col_btn_alt, col_botao_excluir = st.columns([5.5, 1.25, 1.25])
        with col_btn_alt:
            if modo_leitura:
                st.button("🕒 Horário", key=f"btn_alt_bloqueado_{codigo_turno}", disabled=True, use_container_width=True)
            else:
                if st.button("🕒 Horário", key=f"btn_toggle_alt_{codigo_turno}", use_container_width=True, help="Alterar horário da linha selecionada"):
                    if not linhas_selecionadas_idx:
                        st.warning("⚠️ Selecione pelo menos uma linha na tabela.")
                    elif len(linhas_selecionadas_idx) > 1:
                        st.warning("⚠️ Selecione apenas uma linha para alterar o horário.")
                    else:
                        idx_l = linhas_selecionadas_idx[0]
                        if idx_l < len(df_turno_atual):
                            uid_alvo = str(df_turno_atual.iloc[idx_l].get('UID', ''))
                            modal_alterar_horario(uid_alvo, titulo_turno)

        with col_botao_excluir:
            if modo_leitura:
                st.button("🔒 Protegido", key=f"btn_excluir_bloqueado_{codigo_turno}", disabled=True, use_container_width=True, help="Registos anteriores estão protegidos.")
            else:
                if st.button("🗑️ Excluir", key=f"btn_excluir_bloco_{codigo_turno}", use_container_width=True):
                    if linhas_selecionadas_idx:
                        uids_a_remover = []
                        for idx_sel in linhas_selecionadas_idx:
