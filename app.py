import streamlit as st
import random
import pandas as pd

# 1. Configuração Inicial da Página
st.set_page_config(page_title="Bolão Seleção Brasileira", layout="centered")

# Inicialização segura do banco de dados em memória
if "participantes" not in st.session_state:
    st.session_state.participantes = []

if "jogo_atual" not in st.session_state:
    st.session_state.jogo_atual = {
        "confronto": "Brasil x Croácia",
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
    st.subheader(f"Próxima Partida: {st.session_state.jogo_atual['confronto']}")
    
    if st.session_state.jogo_atual["status_finalizado"]:
        st.warning("⚠️ Os palpites para este jogo já estão encerrados.")
    else:
        # Criação correta do formulário com o botão de envio obrigatório dentro do bloco
        with st.form(key="cadastro_palpite", clear_on_submit=True):
            nome = st.text_input("Seu Nome:")
            col1, col2 = st.columns(2)
            with col1:
                gols_br = st.number_input("Gols do Brasil:", min_value=0, step=1, value=0)
            with col2:
                gols_adv = st.number_input("Gols do Adversário:", min_value=0, step=1, value=0)
            
            # O Streamlit exige que este botão esteja EXATAMENTE aqui dentro
            botao_enviar = st.form_submit_button(label="Confirmar Palpite")

        # Processamento após o clique no botão
        if botao_enviar:
            if not nome.strip():
                st.error("❌ Por favor, digite o seu nome antes de enviar.")
            else:
                # Regra: Sorteio aleatório de um jogador de linha
                jogador_sorteado = random.choice(JOGADORES_LINHA)
                
                # Salva o participante na lista do estado da sessão
                st.session_state.participantes.append({
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
    
    # Exibe o placar oficial se o organizador já encerrou o jogo
    if st.session_state.jogo_atual["status_finalizado"]:
        st.info(f" Placar Final Oficial: {st.session_state.jogo_atual['confronto']} "
                f"({st.session_state.jogo_atual['placar_real_br']} x {st.session_state.jogo_atual['placar_real_adv']}) \n\n"
                f"⚽ Último gol do Brasil marcado por: **{st.session_state.jogo_atual['autor_ultimo_gol']}**")
    else:
        st.write("Aguardando a finalização da partida pelo administrador para calcular o ranking.")

    if st.session_state.participantes:
        df = pd.DataFrame(st.session_state.participantes)
        
        # Se o jogo terminou, destaca os vencedores com a regra especial do gol decisivo
        if st.session_state.jogo_atual["status_finalizado"]:
            ganhadores_premio = df[df['acertou_placar_exato'] == True]
            
            # Se houve empate no placar exato ou se ninguém acertou o placar exato
            if len(ganhadores_premio) != 1:
                ganhadores_premio = df[df['ganhou_pelo_jogador'] == True]
            
            if not ganhadores_premio.empty:
                st.subheader("🥇 Ganhador(es) do Prêmio Principal:")
                for _, g in ganhadores_premio.iterrows():
                    motivo = "Placar Exato!" if g['acertou_placar_exato'] else f"Atribuição do jogador decisivo ({g['jogador_atribuido']})!"
                    st.success(f"⭐ **{g['nome']}** levou o prêmio máximo por: *{motivo}*")
        
        st.subheader("📈 Tabela de Pontos")
        st.dataframe(df[["nome", "gols_br", "gols_adv", "jogador_atribuido", "pontos"]].sort_values(by="pontos", ascending=False), use_container_width=True)
    else:
        st.write("Nenhum palpite cadastrado até o momento.")

# ==========================================
# ABA 3: ÁREA DO ADMINISTRADOR (RESTRITA)
# ==========================================
with aba_admin:
    st.header("🔒 Controle do Organizador")
    
    # Senha padrão: brasil2026
    senha = st.text_input("Digite a senha de administrador:", type="password")
    
    if senha == "brasil2026":
        st.success("Acesso autorizado!")
        st.subheader("⚙️ Configurar Partida e Resultados")
        
        # 1. Mudar o nome do próximo confronto
        novo_confronto = st.text_input("Nome do Confronto (Ex: Brasil x França):", value=st.session_state.jogo_atual["confronto"])
        if st.button("Atualizar Nome do Jogo"):
            st.session_state.jogo_atual["confronto"] = novo_confronto
            st.toast("Nome do jogo atualizado!")

        st.markdown("---")
        
        # 2. Inserir o resultado final do jogo
        st.write("📋 **Lançar Placar Final e Fechar Apostas:**")
        res_br = st.number_input("Gols REAIS do Brasil:", min_value=0, step=1, value=0)
        res_adv = st.number_input("Gols REAIS do Adversário:", min_value=0, step=1, value=0)
        
        # Dropdown para escolher o autor do gol da lista oficial
        autor_gol = st.selectbox("Quem fez o ÚLTIMO gol do Brasil?", ["Ninguém"] + JOGADORES_LINHA)
        
        if st.button("🔴 Encerrar Jogo e Calcular Pontos"):
            # Atualiza os dados do jogo real
            st.session_state.jogo_atual["placar_real_br"] = res_br
            st.session_state.jogo_atual["placar_real_adv"] = res_adv
            st.session_state.jogo_atual["autor_ultimo_gol"] = autor_gol
            st.session_state.jogo_atual["status_finalizado"] = True
            
            acertadores_exato = []
            
            # Varre os participantes aplicando os critérios de pontos
            for p in st.session_state.participantes:
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
            
            # Aplica a regra de desempate/vencedor secundário caso não haja um único acertador exato
            if len(acertadores_exato) != 1:
                for p in st.session_state.participantes:
                    if p["jogador_atribuido"] == autor_gol:
                        p["ganhou_pelo_jogador"] = True
            
            st.success("🏆 Pontuações calculadas com sucesso! Verifique a Aba de Classificação Geral.")
            
        st.markdown("---")
        if st.button("🔄 Reiniciar Bolão (Limpar Todos os Palpites)"):
            st.session_state.participantes = []
            st.session_state.jogo_atual["status_finalizado"] = False
            st.rerun()
            
    elif senha != "":
        st.error("❌ Senha incorreta. Tente novamente.")
