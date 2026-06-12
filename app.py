import streamlit as st
import random
import pandas as pd

# 1. Configuração Inicial da Página
st.set_page_config(page_title="Bolão Seleção Brasileira 2026", layout="centered")

# Inicialização segura do banco de dados em memória
if "participantes" not in st.session_state:
    st.session_state.participantes = []

# Dicionário com os dados dos jogos da Fase de Grupos + Opção Customizada
JOGOS_OFICIAIS = {
    "1ª Rodada: Brasil x Marrocos": {"confronto": "Brasil x Marrocos", "bloqueado": False},
    "2ª Rodada: Brasil x Haiti": {"confronto": "Brasil x Haiti", "bloqueado": False},
    "3ª Rodada: Escócia x Brasil": {"confronto": "Escócia x Brasil", "bloqueado": False},
    "Fase Customizada (Mata-Mata)": {"confronto": "Brasil x Adversário", "bloqueado": False}
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

# Lista oficial de jogadores de linha
JOGADORES_LINHA = [
    "Danilo", "Vanderson", "Guilherme Arana", "Abner", "Marquinhos", 
    "Gabriel Magalhães", "Beraldo", "Murilo", "André", "Bruno Guimarães", 
    "Gerson", "Lucas Paquetá", "Raphinha", "Rodrygo", "Vinicius Jr.", 
    "Igor Jesus", "Luiz Henrique", "Savinho", "Andreas Pereira", "Endrick"
]

# Criação das abas de navegação
aba_palpites, aba_ranking, aba_admin = st.tabs(["📝 Dar Palpite", "📊 Classificação Geral", "🔒 Área do Administrador"])

# ==========================================
# ABA 1: PALPITES (PÚBLICO)
# ==========================================
with aba_palpites:
    st.title("🇧🇷 Bolão Exclusivo - Jogos do Brasil")
    st.subheader(f"Partida Ativa: {st.session_state.jogo_atual['confronto']}")
    
    if st.session_state.jogo_atual["status_finalizado"]:
        st.warning("⚠️ Os palpites para este jogo já estão encerrados e o resultado foi lançado.")
    else:
        with st.form(key="cadastro_palpite", clear_on_submit=True):
            nome = st.text_input("Seu Nome:")
            col1, col2 = st.columns(2)
            with col1:
                gols_br = st.number_input("Gols do Brasil:", min_value=0, step=1, value=0)
            with col2:
                gols_adv = st.number_input(f"Gols do Adversário:", min_value=0, step=1, value=0)
            
            botao_enviar = st.form_submit_button(label="Confirmar Palpite")

        if botao_enviar:
            if not nome.strip():
                st.error("❌ Por favor, digite o seu nome antes de enviar.")
            else:
                jogador_sorteado = random.choice(JOGADORES_LINHA)
                
                st.session_state.participantes.append({
                    "jogo": st.session_state.jogo_atual["confronto"],
                    "nome": nome.strip(),
                    "gols_br": gols_br,
                    "gols_adv": gols_adv,
                    "jogador_atribuido": jogador_sorteado,
                    "pontos": 0,
                    "acertou_placar_exato": False,
                    "ganhou_pelo_jogador": False
                })
                st.success(f"✅ {nome}, seu palpite foi registrado! Seu jogador da sorte é: **{jogador_sorteado}**")

# ==========================================
# ABA 2: RANKING E RESULTADO (PÚBLICO)
# ==========================================
with aba_ranking:
    st.header("🏆 Classificação e Resultados")
    
    if st.session_state.jogo_atual["status_finalizado"]:
        st.info(f" Placar Final Oficial: {st.session_state.jogo_atual['confronto']} "
                f"({st.session_state.jogo_atual['placar_real_br']} x {st.session_state.jogo_atual['placar_real_adv']}) \n\n"
                f"⚽ Último gol do Brasil marcado por: **{st.session_state.jogo_atual['autor_ultimo_gol']}**")
    else:
        st.write(f"Aguardando a finalização de **{st.session_state.jogo_atual['confronto']}** para calcular o ranking.")

    if st.session_state.participantes:
        df = pd.DataFrame(st.session_state.participantes)
        
        # Filtra os palpites apenas do jogo que está ativo no momento
        df_filtrado = df[df["jogo"] == st.session_state.jogo_atual["confronto"]]
        
        if not df_filtrado.empty:
            if st.session_state.jogo_atual["status_finalizado"]:
                ganhadores_premio = df_filtrado[df_filtrado['acertou_placar_exato'] == True]
                
                if len(ganhadores_premio) != 1:
                    ganhadores_premio = df_filtrado[df_filtrado['ganhou_pelo_jogador'] == True]
                
                if not ganhadores_premio.empty:
                    st.subheader("🥇 Ganhador(es) do Prêmio Principal deste jogo:")
                    for _, g in ganhadores_premio.iterrows():
                        motivo = "Placar Exato!" if g['acertou_placar_exato'] else f"Atribuição do jogador decisivo ({g['jogador_atribuido']})!"
                        st.success(f"⭐ **{g['nome']}** levou o prêmio por: *{motivo}*")
            
            st.subheader(f"📈 Tabela de Pontos - {st.session_state.jogo_atual['confronto']}")
            st.dataframe(df_filtrado[["nome", "gols_br", "gols_adv", "jogador_atribuido", "pontos"]].sort_values(by="pontos", ascending=False), use_container_width=True)
        else:
            st.write("Nenhum palpite cadastrado para este confronto específico ainda.")
    else:
        st.write("Nenhum palpite cadastrado no sistema.")

# ==========================================
# ABA 3: ÁREA DO ADMINISTRADOR (RESTRITA)
# ==========================================
with aba_admin:
    st.header("🔒 Controle do Organizador")
    senha = st.text_input("Digite a senha de administrador:", type="password")
    
    if senha == "brasil2026":
        st.success("Acesso autorizado!")
        st.subheader("⚙️ Seleção de Rodada e Chaveamento")
        
        # Menu de escolha automática dos jogos
        escolha_jogo = st.selectbox("Selecione qual rodada ativar no sistema:", list(JOGOS_OFICIAIS.keys()), index=list(JOGOS_OFICIAIS.keys()).index(st.session_state.jogo_selecionado_chave))
        
        confronto_final = JOGOS_OFICIAIS[escolha_jogo]["confronto"]
        
        # Se for a opção customizada de mata-mata, libera campo de texto para escrita livre
        if escolha_jogo == "Fase Customizada (Mata-Mata)":
            confronto_final = st.text_input("Digite o confronto customizado (Ex: Brasil x Argentina):", value="Brasil x ")
        
        if st.button("Confirmar e Mudar Jogo Ativo"):
            st.session_state.jogo_selecionado_chave = escolha_jogo
            st.session_state.jogo_atual["confronto"] = confronto_final
            st.session_state.jogo_atual["status_finalizado"] = False
            st.toast(f"Jogo alterado para: {confronto_final}!")
            st.rerun()

        st.markdown("---")
        st.write(f"📋 **Lançar Placar Final para: {st.session_state.jogo_atual['confronto']}**")
        res_br = st.number_input("Gols REAIS do Brasil:", min_value=0, step=1, value=0)
        res_adv = st.number_input("Gols REAIS do Adversário:", min_value=0, step=1, value=0)
        autor_gol = st.selectbox("Quem fez o ÚLTIMO gol do Brasil?", ["Ninguém"] + JOGADORES_LINHA)
        
        if st.button("🔴 Encerrar Jogo e Calcular Pontos"):
            st.session_state.jogo_atual["placar_real_br"] = res_br
            st.session_state.jogo_atual["placar_real_adv"] = res_adv
            st.session_state.jogo_atual["autor_ultimo_gol"] = autor_gol
            st.session_state.jogo_atual["status_finalizado"] = True
            
            acertadores_exato = []
            
            # Varre apenas os palpites do jogo atual para computar os pontos
            for p in st.session_state.participantes:
                if p["jogo"] == st.session_state.jogo_atual["confronto"]:
                    p["acertou_placar_exato"] = (p["gols_br"] == res_br and p["gols_adv"] == res_adv)
                    
                    if p["acertou_placar_exato"]:
                        p["pontos"] = 25
                        acertadores_exato.append(p)
                    elif (p["gols_br"] - p["gols_adv"]) == (res_br - res_adv) and (p["gols_br"] > p["gols_adv"] or p["gols_br"] < p["gols_adv"]):
                        p["pontos"] = 18
                    elif (p["gols_br"] > p["gols_adv"] and res_br > res_adv) or (p["gols_br"] < p["gols_adv"] and res_br < res_adv) or (p["gols_br"] == p["gols_adv"] and res_br == res_adv):
                        p["pontos"] = 10
                    else:
                        p["pontos"] = 0
            
            if len(acertadores_exato) != 1:
                for p in st.session_state.participantes:
                    if p["jogo"] == st.session_state.jogo_atual["confronto"] and p["jogador_atribuido"] == autor_gol:
                        p["ganhou_pelo_jogador"] = True
            
            st.success("🏆 Pontuações calculadas! Confira na Aba de Classificação Geral.")
            
        st.markdown("---")
        if st.button("🔄 Limpar TODOS os palpites salvos no histórico"):
            st.session_state.participantes = []
            st.session_state.jogo_atual["status_finalizado"] = False
            st.rerun()
            
    elif senha != "":
        st.error("❌ Senha incorreta.")
