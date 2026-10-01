import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página para o modo largo (wide)
st.set_page_config(
    page_title="Port Cleanliness Planner - Gestão de Limpeza Industrial",
    page_icon="⚓",
    layout="wide"
)

# Estilização CSS avançada para otimizar o layout e alinhamentos
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
    # PERSISTÊNCIA EM NUVEM (FICHEIRO CSV COMPARTILHADO)
    # ==========================================
    ARQUIVO_BANCO_DADOS = "plano_operacional_nuvem.csv"

    def carregar_plano_nuvem():
        if os.path.exists(ARQUIVO_BANCO_DADOS):
            try:
                df_persisted = pd.read_csv(ARQUIVO_BANCO_DADOS, encoding='utf-8')
                return df_persisted.to_dict(orient='records')
            except:
                pass
        return [
            {
                "ID": "01", 
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
                "ID": "02", 
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

    # Identificar colunas exatas na base
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

        botao_inserir_form = st.form_submit_button("💾 Salvar na Grade", use_container_width=True)

        if botao_inserir_form:
            novo_id = f"{len(st.session_state.plano_operacional) + 1:02d}"
            novo_registro = {
                "ID": novo_id,
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
    # ÁREA PRINCIPAL: GRADES DE PLANEJAMENTO E FILTRO HISTÓRICO
    # ==========================================
    st.markdown("### 📋 Grade de Planejamento Diário Operacional")
    
    df_plano_atual = pd.DataFrame(st.session_state.plano_operacional)
    
    if not df_plano_atual.empty and 'DATA' in df_plano_atual.columns:
        datas_disponiveis = sorted(df_plano_atual['DATA'].dropna().unique().tolist())
    else:
        datas_disponiveis = [datetime.now().strftime('%d/%m/%Y')]

    col_filtro, col_botao_download = st.columns([2, 2])
    with col_filtro:
        data_selecionada_filtro = st.selectbox("🔍 Pesquisar Plano por Data", options=datas_disponiveis, index=len(datas_disponiveis)-1)
    
    df_filtrado_data = df_plano_atual[df_plano_atual['DATA'] == data_selecionada_filtro] if not df_plano_atual.empty else pd.DataFrame()

    with col_botao_download:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
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

    st.markdown("---")

    mapa_cores = {
        "AMARELA": "#FFD700",
        "BRANCA": "#F5F5F5",
        "VERDE": "#32CD32",
        "AZUL": "#1E90FF",
        "ADM": "#A9A9A9"
    }

    # Identifica dinamicamente a cor/turma ativa no Turno Diurno para o dia selecionado
    df_diurno_check = df_filtrado_data[df_filtrado_data['TURNO'].astype(str).str.strip().str.upper() == "DIURNO"] if not df_filtrado_data.empty else pd.DataFrame()
    cor_diurno_herdada = "#FFD700"
    if not df_diurno_check.empty:
        ultima_turma_diurno = str(df_diurno_check.iloc[-1].get('TURMA', 'AMARELA')).strip().upper()
        cor_diurno_herdada = mapa_cores.get(ultima_turma_diurno, "#FFD700")

    turnos_secoes = [
        ("DIURNO", "☀️ Turno Diurno", None),
        ("ADM", "🏢 Turno ADM", cor_diurno_herdada), # ADM herda exatamente a cor do Diurno
        ("NOTURNO", "🌙 Turno Noturno", None)
    ]

    for codigo_turno, titulo_turno, cor_forcada in turnos_secoes:
        df_turno_atual = df_filtrado_data[df_filtrado_data['TURNO'].astype(str).str.strip().str.upper() == codigo_turno] if not df_filtrado_data.empty else pd.DataFrame()
        
        if not df_turno_atual.empty:
            ultima_linha = df_turno_atual.iloc[-1]
            turma_info = str(ultima_linha.get('TURMA', 'N/D')).strip().upper()
            chefe_info = str(ultima_linha.get('CHEFE_TURNO', ultima_linha.get('CHEFE DE TURNO', 'N/D')))
            data_info = str(ultima_linha.get('DATA', data_selecionada_filtro))
            
            # Se for o ADM, a cor do título acompanha estritamente a cor do Diurno
            cor_destaque = cor_forcada if cor_forcada else mapa_cores.get(turma_info, "#FFFFFF")
            
            html_cabecalho = f"""
            <div style="display: flex; align-items: baseline; gap: 15px; margin-bottom: 10px; flex-wrap: wrap;">
                <h4 style="color: {cor_destaque}; margin: 0; padding: 0;">{titulo_turno}</h4>
                <span style="color: #d0d0d0; font-size: 14px;">
                    📌 <b>Turma:</b> <span style="color:{cor_destaque}; font-weight:bold;">{turma_info}</span> 
                    &nbsp;|&nbsp; 👤 <b>Chefe:</b> <span style="color:{cor_destaque};">{chefe_info}</span> 
                    &nbsp;|&nbsp; 📅 <b>Data:</b> <span style="color:{cor_destaque};">{data_info}</span>
                </span>
            </div>
            """
            st.markdown(html_cabecalho, unsafe_allow_html=True)
            
            colunas_exibir = ['Cód. Atividade', 'Hora Inicial', 'Hora Final', 'Ativo', 'Retirada NR12', 'Dados da Atividade', 'Status']
            df_exibicao = df_turno_atual[[c for c in colunas_exibir if c in df_turno_atual.columns]]
            
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
        else:
            cor_destaque = cor_forcada if cor_forcada else "#FFFFFF"
            st.markdown(f"<h4 style='color: {cor_destaque};'>{titulo_turno}</h4>", unsafe_allow_html=True)
            st.info(f"Nenhuma atividade registada no {titulo_turno.lower()} para a data {data_selecionada_filtro}.")
            
        st.markdown("<br>", unsafe_allow_html=True)

    st.divider()

    # ==========================================
    # SEÇÃO DE VISUALIZAÇÃO DOS DADOS BRUTOS DA BASE
    # ==========================================
    st.subheader("📑 Base de Ordens de Serviço Processadas (Referência)")
    st.dataframe(df_os.head(50), use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar o sistema: {e}")
