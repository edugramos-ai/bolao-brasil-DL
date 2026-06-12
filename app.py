import streamlit as st
import random
import pandas as pd

# 1. Configuração Inicial e Banco de Dados em Memória
st.set_page_config(page_title="Bolão Seleção Brasileira", layout="centered")

if "participantes" not in st.session_state:
    st.session_state.participantes = []

# Lista oficial de jogadores de linha (excluindo goleiros)
JOGADORES_LINHA = [
    "Danilo", "Vanderson", "Guilherme Arana", "Abner", "Marquinhos", 
    "Gabriel Magalhães", "Beraldo", "Murilo", "André", "Bruno Guimarães", 
    "Gerson", "Lucas Paquetá", "Raphinha", "Rodrygo", "Vinicius Jr.", 
    "Igor Jesus", "Luiz Henrique", "Savinho", "Andreas Pereira", "Endrick"
]

# Dados fictícios do jogo atual para teste do sistema
JOGO_ATUAL = {"confronto": "Brasil x Croácia", "placar_real_br": 2, "placar_real_adv": 1, "autor_ultimo_gol": "Raphinha"}

st.title("🇧🇷 Bolão Exclusivo - Jogos do Brasil")
st.markdown("---")

# 2. Tela de Cadastro e Palpite
st.header("📝 Cadastrar seu Palpite")
with st.form("cadastro_palpite", clear_on_submit=True):
    nome = st.text_input("Seu Nome:")
    col1, col2 = st.columns(2)
    with col1:
        gols_br = st.number_input("Gols do Brasil:", min_value=0, step=1, value=0)
   # ==========================================
# ABA 1: PALPITES (PÚBLICO)
# ==========================================
with aba_palpites:
    st.title("🇧🇷 Bolão Exclusivo - Jogos do Brasil")
    st.subheader(f"Próxima Partida: {st.session_state.jogo_atual['confronto']}")
    
    if st.session_state.jogo_atual["status_finalizado"]:
        st.warning("⚠️ Os palpites para este jogo já estão encerrados.")
    else:
        with st.form("cadastro_palpite", clear_on_submit=True):
            nome = st.text_input("Seu Nome:")
            col1, col2 = st.columns(2)
            with col1:
                gols_br = st.number_input("Gols do Brasil:", min_value=0, step=1, value=0)
            with col2:
                gols_adv = st.number_input("Gols do Adversário:", min_value=0, step=1, value=0)
            
            botao_enviar = st.form_submit_button("Confirmar Palpite")

        if botao_enviar:
            if not nome.strip():
                st.error("❌ Por favor, digite o seu nome.")
            else:
                # Regra: Sorteio aleatório de um jogador de linha
                jogador_sorteado = random.choice(JOGADORES_LINHA)
                
                # Salva o participante na lista
                st.session_state.participantes.append({
                    "nome": nome,
                    "gols_br": gols_br,
                    "gols_adv": gols_adv,
                    "jogador_atribuido": jogador_sorteado,
                    "pontos": 0,
                    "acertou_placar_exato": False,
                    "ganhou_pelo_jogador": False
                })
                st.success(f"✅ {nome}, seu palpite foi registrado! Seu jogador da sorte é: **{jogador_sorteado}**")

if st.button("📊 Calcular Pontuações e Vencedor"):
    br_real = JOGO_ATUAL["placar_real_br"]
    adv_real = JOGO_ATUAL["placar_real_adv"]
    autor_gol_real = JOGO_ATUAL["autor_ultimo_gol"]
    
    acertadores_exato = []
    
    # Passo 1: Calcular pontuação padrão e identificar acertos exatos
    for p in st.session_state.participantes:
        p["acertou_placar_exato"] = (p["gols_br"] == br_real and p["gols_adv"] == adv_real)
        
        if p["acertou_placar_exato"]:
            p["pontos"] = 25
            acertadores_exato.append(p)
        elif (p["gols_br"] - p["gols_adv"]) == (br_real - adv_real) and (p["gols_br"] > p["gols_adv"] or p["gols_br"] < p["gols_adv"]):
            p["pontos"] = 18  # Diferença de gols
        elif (p["gols_br"] > p["gols_adv"] and br_real > adv_real) or (p["gols_br"] < p["gols_adv"] and br_real < adv_real) or (p["gols_br"] == p["gols_adv"] and br_real == adv_real):
            p["pontos"] = 10  # Resultado seco
        else:
            p["pontos"] = 0
            
    # Passo 2: Aplicar a Nova Regra do Jogador Decisivo
    # Condição: Se ninguém acertou o placar exato OU se mais de uma pessoa acertou
    if len(acertadores_exato) != 1:
        for p in st.session_state.participantes:
            if p["jogador_atribuido"] == autor_gol_real:
                p["ganhou_pelo_jogador"] = True
                
# 4. Exibição do Ranking e Ganhadores
if st.session_state.participantes:
    df = pd.DataFrame(st.session_state.participantes)
    
    # Destacar o ganhador do prêmio principal baseado na nova regra
    ganhadores_premio = df[df['acertou_placar_exato'] == True]
    
    if len(ganhadores_premio) != 1:
        # Se houve empate ou nenhum acerto exato, busca quem tem o jogador do gol decisivo
        ganhadores_premio = df[df['ganhou_pelo_jogador'] == True]
    
    if not ganhadores_premio.empty:
        st.subheader("🏆 Ganhador(es) do Prêmio Principal:")
        for _, g in ganhadores_premio.iterrows():
            motivo = "Placar Exato!" if g['acertou_placar_exato'] else f"Atribuição do jogador decisivo ({g['jogador_atribuido']})!"
            st.balloons()
            st.markdown(f"🥇 **{g['nome']}** venceu por: *{motivo}*")
            
    st.subheader("📈 Classificação Geral")
    st.dataframe(df[["nome", "gols_br", "gols_adv", "jogador_atribuido", "pontos"]].sort_values(by="pontos", ascending=False))
else:
    st.write("Nenhum palpite cadastrado ainda.")
