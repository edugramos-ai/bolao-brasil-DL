import streamlit as st
import random
import pandas as pd

# 1. Configuração e Estilização Visual (Verde e Amarelo)
st.set_page_config(page_title="Bolão Seleção Brasileira 2026", layout="centered")

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #009c3b !important;
        color: #ffdf00 !important;
        font-weight: bold;
    }
    div[data-testid="stHeader"] {
        background-color: #009c3b;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização segura do banco de dados em memória
if "participantes" not in st.session_state:
    st.session_state.participantes = []

# Agenda oficial Copa 2026
JOGOS_OFICIAIS = {
    "1ª Rodada: Brasil x Marrocos": {"confronto": "Brasil x Marrocos"},
    "2ª Rodada: Brasil x Haiti": {"confronto": "Brasil x Haiti"},
    "3ª Rodada: Escócia x Brasil": {"confronto": "Escócia x Brasil"},
    "Fase Customizada (Mata-Mata)": {"confronto": "Brasil x Adversário"}
}

if "jogo_selecionado_chave" not in st.session_state:
    st.session_state.jogo_selecionado_chave = "1ª Rodada: Brasil x Marrocos"

if "jogo_atual" not in st.session_state:
    st.session_state.jogo_atual = {
        "confronto": JOGOS_OFICIAIS[st.session_state.jogo_selecionado_chave]["confronto"],
        "placar_real_br": 0,
        "placar_real_adv": 0,
        "autor_ultimo_gol": "Ninguém",
        "status_finalizado": False
    }

# Lista DEFINITIVA de jogadores de linha convocados (Copa 2026)
JOGADORES_LINHA = [
    "Alex Sandro", "Bremer", "Danilo", "Douglas Santos", 
    "Gabriel Magalhães", "Ibañez", "Léo Pereira", "Marquinhos", "Wesley",
    "Bruno Guimarães", "Casemiro", "Danilo (Botafogo)", "Fabinho", "Lucas Paquetá",
    "Endrick", "Gabriel Martinelli", "Igor Thiago", "Luiz Henrique", 
    "Matheus Cunha", "Neymar", "Raphinha", "Rayan", "Vini Jr."
]

# Abas de navegação
aba_palpites, aba_ranking, aba_admin = st.tabs(["📝 DAR PALPITE", "📊 CLASSIFICAÇÃO", "🔒 ADMINISTRADOR"])

# ==========================================
# ABA 1: PALPITES
# ==========================================
with aba_palpites:
    st.markdown("<h1 style='text-align: center; color: #009c3b;'>🇧🇷 Bolão Copa 2026 🇧🇷</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #111;'>Partida Ativa: <b>{st.session_state.jogo_atual['confronto']}</b></h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.jogo_atual["status_finalizado"]:
        st.warning("⚠️ Os palpites para este jogo já estão encerrados e o resultado foi lançado.")
    else:
        with st.form(key="cadastro_palpite", clear_on_submit=True):
            nome = st.text_input("Seu Nome:")
            col1, col2 = st.columns(2)
            with col1:
                gols_br = st.number_input("Gols do Brasil:", min_value=0, step=1, value=0)
            with col2:
                gols_adv = st.number_input("Gols do Adversário:", min_value=0, step=1, value=0)
            
            botao_enviar = st.form_submit_button(label="🚀 ENVIAR PALPITE")

        if botao_enviar:
            if not nome.strip():
                st.error("❌ Por favor, digite o seu nome antes de enviar.")
            else:
                nome_limpo = nome.strip().title()
                ja_votou = any(p["nome"] == nome_limpo and p["jogo"] == st.session_state.jogo_atual["confronto"] for p in st.session_state.participantes)
                
                if ja_votou:
                    st.error(f"❌ {nome_limpo}, você já cadastrou um palpite para o jogo {st.session_state.jogo_atual['confronto']}!")
                else:
                    jogador_sorteado = random.choice(JOGADORES_LINHA)
                    st.session_state.participantes.append({
                        "jogo": st.session_state.jogo_atual["confronto"],
                        "nome": nome_limpo,
                        "gols_br": gols_br,
                        "gols_adv": gols_adv,
                        "jogador_atribuido": App_Var if 'App_Var' in locals() else jogador_sorteado,
                        "pontos": 0,
                        "acertou_placar_exato": False,
                        "ganhou_pelo_jogador": False
                    })
                    st.balloons()
                    st.success(f"✅ {nome_limpo}, palpite salvo! Seu jogador da sorte é: **{jogador_sorteado}**")

# ==========================================
# ABA 2: RANKINGS (RODADA + GERAL)
# ==========================================
with aba_ranking:
    st.markdown("<h2 style='color: #009c3b;'>🏆 Classificação Geral e Resultados</h2>", unsafe_allow_html=True)
    
    if st.session_state.jogo_atual["status_finalizado"]:
        st.info(f" Placar Final: {st.session_state.jogo_atual['confronto']} "
                f"({st.session_state.jogo_atual['placar_real_br']} x {st.session_state.jogo_atual['placar_real_adv']}) \n\n"
                f"⚽ Último gol do Brasil: **{st.session_state.jogo_atual['autor_ultimo_gol']}**")
    else:
        st.write(f"Aguardando o fim de **{st.session_state.jogo_atual['confronto']}**.")

    if st.session_state.participantes:
        df = pd.DataFrame(st.session_state.participantes)
        
        st.markdown("<h4 style='color: #009c3b; margin-top:20px;'>⚽ Palpites da Rodada Ativa</h4>", unsafe_allow_html=True)
        df_filtrado = df[df["jogo"] == st.session_state.jogo_atual["confronto"]]
        
        if not df_filtrado.empty:
            if st.session_state.jogo_atual["status_finalizado"]:
                ganhadores_premio = df_filtrado[df_filtrado['acertou_placar_exato'] == True]
                if len(ganhadores_premio) != 1:
                    ganhadores_premio = df_filtrado[df_filtrado['ganhou_pelo_jogador'] == True]
                
                if not ganhadores_premio.empty:
                    st.subheader("🥇 Ganhador(es) do Prêmio da Rodada:")
                    for _, g in ganhadores_premio.iterrows():
                        motivo = "Placar Exato!" if g['acertou_placar_exato'] else f"Jogador Decisivo ({g['jogador_atribuido']})!"
                        st.success(f"⭐ **{g['nome']}** venceu por: *{motivo}*")
            
            st.dataframe(df_filtrado[["nome", "gols_br", "gols_adv", "jogador_atribuido", "pontos"]].sort_values(by="pontos", ascending=False), use_container_width=True)
        else:
            st.write("Sem palpites para o confronto ativo.")
            
        st.markdown("<h4 style='color: #ffdf00; background-color:#009c3b; padding: 5px 10px; border-radius:4px;'>📈 CLASSIFICAÇÃO GERAL DO TORNEIO (Soma de tudo)</h4>", unsafe_allow_html=True)
        df_geral = df.groupby("nome")["pontos"].sum().reset_index()
        df_geral.columns = ["Nome do Participante", "Pontos Totais Acumulados"]
        
        st.dataframe(df_geral.sort_values(by="Pontos Totais Acumulados", ascending=False), use_container_width=True)
    else:
        st.write("Nenhum palpite cadastrado no sistema ainda.")

# ==========================================
# ABA 3: ADMINISTRADOR
# ==========================================
with aba_admin:
    st.header("🔒 Painel do Organizador")
    senha = st.text_input("Senha de administrador:", type="password")
    
    if senha == "brasil2026":
        st.success("Acesso autorizado!")
        
        st.subheader("💾 Backup de Segurança")
        if st.session_state.participantes:
            df_backup = pd.DataFrame(st.session_state.participantes)
            csv_data = df_backup.to_csv(index=False)
            
            st.download_button(
                label="📥 Baixar Planilha de Palpites (CSV)",
                data=csv_data,
                file_name="backup_bolao_brasil_2026.csv",
                mime="text/csv",
            )
            st.caption("Dica: Baixe este arquivo antes de resetar o app ou ao fim de cada rodada.")
        else:
            st.info("Nenhum dado cadastrado para exportar ainda.")
        st.markdown("---")
        
        st.subheader("⚙️ Gerenciar Rodadas")
        escolha_jogo = st.selectbox("Ativar qual jogo no sistema?", list(JOGOS_OFICIAIS.keys()), index=list(JOGOS_OFICIAIS.keys()).index(st.session_state.jogo_selecionado_chave))
        confronto_final = JOGOS_OFICIAIS[escolha_jogo]["confronto"]
        
        if escolha_jogo == "Fase Customizada (Mata-Mata)":
            confronto_final = st.text_input("Digite o confronto (Ex: Brasil x Argentina):", value="Brasil x ")
        
        if st.button("Confirmar Mudança de Jogo"):
            st.session_state.jogo_selecionado_chave = escolha_jogo
            st.session_state.jogo_atual["confronto"] = confronto_final
            st.session_state.jogo_atual["status_finalizado"] = False
            st.toast(f"Jogo alterado para: {confronto_final}!")
            st.rerun()

        st.markdown("---")
        st.write(f"📋 **Encerrar e Pontuar: {st.session_state.jogo_atual['confronto']}**")
        res_br = st.number_input("Gols REAIS do Brasil:", min_value=0, step=1, value=0)
        res_adv = st.number_input("Gols REAIS do Adversário:", min_value=0, step=1, value=0)
        autor_gol = st.selectbox("Quem fez o ÚLTIMO gol do Brasil?", ["Ninguém"] + JOGADORES_LINHA)
        
        if st.button("🔴 Fechar Rodada e Computar Pontos"):
            st.session_state.jogo_atual["placar_real_br"] = res_br
            st.session_state.jogo_atual["placar_real_adv"] = res_adv
            st.session_state.jogo_atual["autor_ultimo_gol"] = autor_gol
            st.session_state.jogo_atual["status_finalizado"] = True
            
            acertadores_exato = []
            
            for p in st.session_state.participantes:


