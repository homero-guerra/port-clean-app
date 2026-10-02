import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# Configuração da página para o modo largo (wide)
st.set_page_config(
    page_title="Plano de Limpeza Ferroport - Gestão de Limpeza Industrial",
    page_icon="✨",
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

# Estilização CSS avançada para alinhamentos e estética corporativa
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
    
    /* Remover espaçamento superior da página principal */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }
    
    div[data-testid="stButton"] button { font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Título principal do painel alinhado no topo absoluto com o novo emoji ✨
st.markdown("<h1>✨ Plano de Limpeza Ferroport</h1>", unsafe_allow_html=True)
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
    # PERSISTÊNCIA EM NUVEM (FICHEIRO CSV COMPARTILHADO)
    # ==========================================
    ARQUIVO_BANCO_DADOS = "plano_operacional_nuvem.csv"

    def carregar_plano_nuvem():
        if os.path.exists(ARQUIVO_BANCO_DADOS):
            try:
                df_persisted = pd.read_csv(ARQUIVO_BANCO_DADOS, encoding='utf-8')
                if 'UID' not in df_persisted.columns:
                    df_persisted['UID'] = [f"UID_{i}_{int(datetime.now().timestamp())}" for i in range(len(df_persisted))]
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
                "Status": "Em Execução"
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
                "Status": "Em Execução"
            }
        ]

    def salvar_plano_nuvem(lista_registros):
        df_to_save = pd.DataFrame(lista_registros)
        df_to_save.to_csv(ARQUIVO_BANCO_DADOS, index=False, encoding='utf-8')

    # ==========================================
    # GESTÃO DO ESTADO DA SESSÃO
    # ==========================================
    if 'lista_chefes' not in st.session_state:
        chefes_iniciais = df_os['CHEFE_TURNO'].dropna().unique().tolist() if 'CHEFE_TURNO' in df_os.columns else ["20000000 - GERSON FUENTES", "20005373 - TEMISTOCLES SANTANA"]
        st.session_state.lista_chefes = sorted(list(set(chefes_iniciais)))

    if 'plano_operacional' not in st.session_state:
        st.session_state.plano_operacional = carregar_plano_nuvem()

    col_cod = 'COD. ATIVIDADE' if 'COD. ATIVIDADE' in df_os.columns else 'COD_ATIVIDADE'
    col_desc = 'ATIVIDADE' if 'ATIVIDADE' in df_os.columns else df_os.columns[-1]
    col_ativo = 'ATIVO' if 'ATIVO' in df_os.columns else (df_os.columns[6] if len(df_os.columns) > 6 else df_os.columns[0])

    if col_cod in df_os.columns and col_desc in df_os.columns:
        df_unicos = df_os[[col_cod, col_desc]].dropna().drop_duplicates(subset=[col_cod])
        lista_opcoes_atividades = sorted([f"{row[col_cod]} - {row[col_desc]}" for _, row in df_unicos.iterrows()])
    else:
        lista_opcoes_atividades = ["3230TR02.1 - LAVAGEM DA ESTRUTURA DA CALDA DA 3230TR02", "CT08.4 - CONTINUAR RECHEGO NA A4"]

    # ==========================================
    # BARRA LATERAL: MENU DE PLANEJAMENTO
    # ==========================================
    st.sidebar.markdown("### 🎛️ MENU DE PLANEJAMENTO")

    with st.sidebar.form("form_inserir_atividade"):
        
        col_d, col_h1, col_h2 = st.columns([2, 1, 1])
        with col_d:
            data_stamp = st.date_input("Data", value=datetime.now().date())
        with col_h1:
            hora_ini_form = st.text_input("Hora Inicial", value="07:00")
        with col_h2:
            hora_fim_form = st.text_input("Hora Final", value="08:00")
            
        st.markdown("---")
        
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

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            turma_form = st.selectbox("Turma / Equipe", options=["AMARELA", "BRANCA", "VERDE", "AZUL", "ADM"])
        with col_t2:
            turno_form = st.selectbox("Turno", options=["DIURNO", "ADM", "NOTURNO"])

        # Injetar cor dinâmica baseada na Turma selecionada de forma segura
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

        botao_inserir_form = st.form_submit_button("💾 Incluir na Grade", use_container_width=True)

        if botao_inserir_form:
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
                "Status": "Agendado"
            }
            st.session_state.plano_operacional.append(novo_registro)
            salvar_plano_nuvem(st.session_state.plano_operacional)
            st.success(f"Adicionado e salvo com sucesso no Turno {turno_form}!")
            st.rerun()

    # ==========================================
    # ÁREA PRINCIPAL: TÍTULO, FILTRO E BOTÃO DE DOWNLOAD ALINHADOS
    # ==========================================
    df_plano_atual = pd.DataFrame(st.session_state.plano_operacional)
    
    if not df_plano_atual.empty and 'DATA' in df_plano_atual.columns:
        datas_disponiveis = sorted(df_plano_atual['DATA'].dropna().unique().tolist())
    else:
        datas_disponiveis = [datetime.now().strftime('%d/%m/%Y')]

    col_tit_grade, col_filtro_grade, col_down_grade = st.columns([4, 2, 2])
    with col_tit_grade:
        st.markdown("### 📋 Grade de Planejamento Diário")
    with col_filtro_grade:
        data_selecionada_filtro = st.selectbox("🔍 Pesquisar Plano por Data", options=datas_disponiveis, index=len(datas_disponiveis)-1, label_visibility="collapsed")
    with col_down_grade:
        df_filtrado_data = df_plano_atual[df_plano_atual['DATA'] == data_selecionada_filtro] if not df_plano_atual.empty else pd.DataFrame()
        if not df_filtrado_data.empty:
            csv_export = df_filtrado_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Plano do Dia (CSV)",
                data=csv_export,
                file_name=f"Plano_Operacional_{data_selecionada_filtro.replace('/', '-')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("📥 Baixar Plano do Dia (CSV)", disabled=True, use_container_width=True)

    # ==========================================
    # CAMPO: LISTA DE DISTRIBUIÇÃO E INTEGRAÇÃO OUTLOOK
    # ==========================================
    col_lbl_dist, col_input_email, col_btn_email = st.columns([1.5, 5.5, 1.0])
    with col_lbl_dist:
        st.markdown("<div style='margin-top: 10px; font-weight: 600; font-size: 14px;'>Lista de Distribuição:</div>", unsafe_allow_html=True)
    with col_input_email:
        lista_emails = st.text_input("Destinatários", value="operacao.limpeza@ferroport.com.br, supervisao.pcp@ferroport.com.br, gerencia.operacional@ferroport.com.br", label_visibility="collapsed")
    with col_btn_email:
        btn_enviar_outlook = st.button("✉️ Enviar Plano", use_container_width=True)

    if btn_enviar_outlook:
        assunto = f"[Ferroport] Plano de Limpeza Operacional - {data_selecionada_filtro}"
        corpo = f"""Prezados(as),

Segue em anexo o relatório oficial consolidado do Plano de Limpeza Diário correspondente à data {data_selecionada_filtro}.

Atenciosamente,
Gerência de Operações / PCP Ferroport"""
        
        # Codificar assunto e corpo para URL (protocolo mailto)
        assunto_encoded = urllib.parse.quote(assunto)
        corpo_encoded = urllib.parse.quote(corpo)
        
        # Montar link mailto direcionando para o Outlook / Cliente de e-mail padrão
        mailto_link = f"mailto:{lista_emails}?subject={assunto_encoded}&body={corpo_encoded}"
        
        st.markdown(f'<meta http-equiv="refresh" content="0;url={mailto_link}">', unsafe_allow_html=True)
        st.success("Outlook acionado! A mensagem foi aberta com os destinatários preenchidos para revisão.")

    st.markdown("---")

    turnos_secoes = [
        ("DIURNO", "☀️ Turno Diurno"),
        ("ADM", "🏢 Turno ADM"),
        ("NOTURNO", "🌙 Turno Noturno")
    ]

    for codigo_turno, titulo_turno in turnos_secoes:
        df_turno_atual = df_filtrado_data[df_filtrado_data['TURNO'].astype(str).str.strip().str.upper() == codigo_turno] if not df_filtrado_data.empty else pd.DataFrame()
        
        if not df_turno_atual.empty:
            ultima_linha = df_turno_atual.iloc[-1]
            turma_info = str(ultima_linha.get('TURMA', 'N/D')).strip().upper()
            chefe_info = str(ultima_linha.get('CHEFE_TURNO', ultima_linha.get('CHEFE DE TURNO', 'N/D')))
            data_info = str(ultima_linha.get('DATA', data_selecionada_filtro))
            
            if codigo_turno == "ADM":
                cor_destaque = "#FFFFFF"
            else:
                cor_destaque = mapa_cores.get(turma_info, "#FFFFFF")
            
            selecao_key = f"dataframe_grid_{codigo_turno}_{data_selecionada_filtro}"
            
            col_titulo_bloco, col_vazio_bloco, col_botao_excluir = st.columns([5, 1.0, 1.4])
            with col_titulo_bloco:
                html_cabecalho = f"""
                <div style="display: flex; align-items: baseline; gap: 15px; flex-wrap: wrap;">
                    <h4 style="color: {cor_destaque}; margin: 0; padding: 0;">{titulo_turno}</h4>
                    <span style="color: #d0d0d0; font-size: 14px;">
                        👥 <b>Equipe:</b> <span style="color:{cor_destaque}; font-weight:bold;">{turma_info}</span> 
                        &nbsp;|&nbsp; 👤 <b>Chefe:</b> <span style="color:{cor_destaque};">{chefe_info}</span> 
                        &nbsp;|&nbsp; 📅 <b>Data:</b> <span style="color:{cor_destaque};">{data_info}</span>
                    </span>
                </div>
                """
                st.markdown(html_cabecalho, unsafe_allow_html=True)
            
            with col_botao_excluir:
                if st.button("🗑️ Excluir Linha", key=f"btn_excluir_bloco_{codigo_turno}", use_container_width=True):
                    estado_grid = st.session_state.get(selecao_key, {})
                    linhas_selecionadas = estado_grid.get("selection", {}).get("rows", [])
                    
                    if linhas_selecionadas:
                        uids_a_remover = []
                        for idx_sel in linhas_selecionadas:
                            if idx_sel < len(df_turno_atual):
                                uid_item = str(df_turno_atual.iloc[idx_sel].get('UID', ''))
                                if uid_item:
                                    uids_a_remover.append(uid_item)
                        
                        if uids_a_remover:
                            st.session_state.plano_operacional = [item for item in st.session_state.plano_operacional if str(item.get('UID')) not in uids_a_remover]
                            salvar_plano_nuvem(st.session_state.plano_operacional)
                            
                            if selecao_key in st.session_state:
                                del st.session_state[selecao_key]
                            st.session_state[selecao_key] = {"selection": {"rows": []}}
                                
                            st.success(f"{len(uids_a_remover)} linha(s) excluída(s) com sucesso!")
                            st.rerun()
                    else:
                        st.warning("Selecione pelo menos uma linha na tabela.")

            df_exibicao = df_turno_atual.copy()
            if 'UID' not in df_exibicao.columns:
                df_exibicao['UID'] = [f"UID_{i}" for i in range(len(df_exibicao))]
                
            df_exibicao.insert(0, 'Nº', range(1, len(df_exibicao) + 1))
            
            colunas_exibir = ['Nº', 'UID', 'Cód. Atividade', 'Hora Inicial', 'Hora Final', 'Ativo', 'Retirada NR12', 'Dados da Atividade', 'Status']
            df_final_exibir = df_exibicao[[c for c in colunas_exibir if c in df_exibicao.columns]]
            
            st.dataframe(
                df_final_exibir,
                use_container_width=True,
                hide_index=True,
                selection_mode="multi-row",
                on_select="rerun",
                column_config={
                    "Nº": st.column_config.NumberColumn("Nº", width="small"),
                    "UID": None
                },
                key=selecao_key
            )
            
        else:
            st.markdown(f"<h4>{titulo_turno}</h4>", unsafe_allow_html=True)
            st.info(f"Nenhuma atividade registada no {titulo_turno.lower()} para a data {data_selecionada_filtro}.")
            
        st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao carregar o sistema: {e}")
