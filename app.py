import streamlit as st
import random
import pandas as pd
import requests

# 1. Configuração e Estilização Visual
st.set_page_config(page_title="Bolão Seleção Brasileira 2026", layout="centered")
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap; background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px; gap: 1px; padding: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #009c3b !important; color: #ffdf00 !important; font-weight: bold;
    }
    div[data-testid="stHeader"] { background-color: #009c3b; }
    </style>
""", unsafe_allow_html=True)

# Credenciais coletadas dos Secrets
AIRTABLE_TOKEN = st.secrets["airtable"]["token"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_ID = st.secrets["airtable"]["table_id"]
URL = f"https://airtable.com{BASE_ID}/{TABLE_ID}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}

def ler_dados():
    response = requests.get(URL, headers=HEADERS)
    if response.status_code == 200:
        records = response.json().get("records", [])
        if not records:
            return pd.DataFrame(columns=["id", "jogo", "nome", "gols_br", "gols_adv", "jogador_atribuido", "pontos", "acertou_placar_exato", "ganhou_pelo_jogador"])
        dados = []
        for r in records:
            f = r.get("fields", {})
            f["id"] = r.get("id")
            dados.append(f)
        df = pd.DataFrame(dados)
        df["gols_br"] = pd.to_numeric(df.get("gols_br", 0), errors='coerce').fillna(0).astype(int)
        df["gols_adv"] = pd.to_numeric(df.get("gols_adv", 0), errors='coerce').fillna(0).astype(int)
        df["pontos"] = pd.to_numeric(df.get("pontos", 0), errors='coerce').fillna(0).astype(int)
        return df
    return pd.DataFrame(columns=["id", "jogo", "nome", "gols_br", "gols_adv", "jogador_atribuido", "pontos", "acertou_placar_exato", "ganhou_pelo_jogador"])

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
        "placar_real_br": 0, "placar_real_adv": 0, "autor_ultimo_gol": "Ninguém", "status_finalizado": False
    }

JOGADORES_LINHA = [
    "Alex Sandro", "Bremer", "Danilo", "Douglas Santos", "Gabriel Magalhães", 
    "Ibañez", "Léo Pereira", "Marquinhos", "Wesley", "Bruno Guimarães", 
    "Casemiro", "Danilo (Botafogo)", "Fabinho", "Lucas Paquetá", "Endrick", 
    "Gabriel Martinelli", "Igor Thiago", "Luiz Henrique", "Matheus Cunha", 
    "Neymar", "Raphinha", "Rayan", "Vini Jr."
]

aba_palpites, aba_ranking, aba_admin = st.tabs(["📝 DAR PALPITE", "📊 CLASSIFICAÇÃO", "🔒 ADMINISTRADOR"])

with aba_palpites:
    st.markdown("<h1 style='text-align: center; color: #009c3b;'>🇧🇷 Bolão Copa 2026 🇧🇷</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>Partida Ativa: <b>{st.session_state.jogo_atual['confronto']}</b></h3>", unsafe_allow_html=True)
    
    if st.session_state.jogo_atual["status_finalizado"]:
        st.warning("⚠️ Os palpites para este jogo já estão encerrados.")
    else:
        with st.form(key="cadastro_palpite", clear_on_submit=True):
            nome = st.text_input("Seu Nome:")
            col1, col2 = st.columns(2)
            with col1: gols_br = st.number_input("Gols do Brasil:", min_value=0, step=1, value=0)
            with col2: gols_adv = st.number_input("Gols do Adversário:", min_value=0, step=1, value=0)
            botao_enviar = st.form_submit_button(label="🚀 ENVIAR PALPITE")

        if botao_enviar and nome.strip():
            nome_limpo = nome.strip().title()
            df_atual = ler_dados()
            ja_votou = False
            if not df_atual.empty and "jogo" in df_atual.columns:
                ja_votou = ((df_atual["nome"] == nome_limpo) & (df_atual["jogo"] == st.session_state.jogo_atual["confronto"])).any()
            
            if ja_votou:
                st.error(f"❌ {nome_limpo}, você já palpitou neste jogo!")
            else:
                jogador_sorteado = random.choice(JOGADORES_LINHA)
                payload = {"fields": {
                    "jogo": st.session_state.jogo_atual["confronto"], "nome": nome_limpo,
                    "gols_br": str(int(gols_br)), "gols_adv": str(int(gols_adv)),
                    "jogador_atribuido": jogador_sorteado, "pontos": "0",
                    "acertou_placar_exato": "False", "ganhou_pelo_jogador": "False"
                }}
                requests.post(URL, headers=HEADERS, json=payload)
                st.balloons()
                st.success(f"✅ {nome_limpo}! Seu jogador é: {jogador_sorteado}")

with aba_ranking:
    st.markdown("<h2 style='color: #009c3b;'>🏆 Classificação Geral e Resultados</h2>", unsafe_allow_html=True)
    if st.session_state.jogo_atual["status_finalizado"]:
        st.info(f"Placar Final: {st.session_state.jogo_atual['confronto']} ({st.session_state.jogo_atual['placar_real_br']}x{st.session_state.jogo_atual['placar_real_adv']}) | Último gol: {st.session_state.jogo_atual['autor_ultimo_gol']}")
    
    df_nuvem = ler_dados()
    if not df_nuvem.empty and "jogo" in df_nuvem.columns:
        df_filtrado = df_nuvem[df_nuvem["jogo"] == st.session_state.jogo_atual["confronto"]]
        if not df_filtrado.empty:
            st.dataframe(df_filtrado[["nome", "gols_br", "gols_adv", "jogador_atribuido", "pontos"]].sort_values(by="pontos", ascending=False), use_container_width=True)
        
        df_geral = df_nuvem.groupby("nome")["pontos"].sum().reset_index()
        df_geral.columns = ["Nome do Participante", "Pontos Totais Acumulados"]
        st.dataframe(df_geral.sort_values(by="Pontos Totais Acumulados", ascending=False), use_container_width=True)
    else:
        st.write("Nenhum palpite cadastrado.")

with aba_admin:
    st.header("🔒 Painel do Organizador")
    senha = st.text_input("Senha de administrador:", type="password")
    if senha == "brasil2026":
        st.success("Acesso autorizado!")
        escolha_jogo = st.selectbox("Ativar qual jogo?", list(JOGOS_OFICIAIS.keys()), index=list(JOGOS_OFICIAIS.keys()).index(st.session_state.jogo_selecionado_chave))
        confronto_final = JOGOS_OFICIAIS[escolha_jogo]["confronto"]
        if escolha_jogo == "Fase Customizada (Mata-Mata)":
            confronto_final = st.text_input("Digite o confronto:", value="Brasil x ")
        
        if st.button("Confirmar Mudança de Jogo"):
            st.session_state.jogo_selecionado_chave = escolha_jogo
            st.session_state.jogo_atual["confronto"] = confronto_final
            st.session_state.jogo_atual["status_finalizado"] = False
            st.rerun()

        res_br = st.number_input("Gols REAIS do Brasil:", min_value=0, step=1, value=0)
        res_adv = st.number_input("Gols REAIS do Adversário:", min_value=0, step=1, value=0)
        autor_gol = st.selectbox("Último gol do Brasil:", ["Ninguém"] + JOGADORES_LINHA)
        
        if st.button("🔴 Fechar Rodada e Computar Pontos"):
            st.session_state.jogo_atual["placar_real_br"] = res_br
            st.session_state.jogo_atual["placar_real_adv"] = res_adv
            st.session_state.jogo_atual["autor_ultimo_gol"] = autor_gol
            st.session_state.jogo_atual["status_finalizado"] = True
            
            df_calculo = ler_dados()
            if not df_calculo.empty:
                acertadores_exato = []
                for idx, row in df_calculo.iterrows():
                    if row["jogo"] == st.session_state.jogo_atual["confronto"]:
                        exato = (int(row["gols_br"]) == res_br and int(row["gols_adv"]) == res_adv)
                        pt = 0
                        if exato:
                            pt = 25
                            acertadores_exato.append(row["id"])
                        elif (int(row["gols_br"]) - int(row["gols_adv"])) == (res_br - res_adv) and (int(row["gols_br"]) > int(row["gols_adv"]) or int(row["gols_br"]) < int(row["gols_adv"])):
                            pt = 18
                        elif (int(row["gols_br"]) > int(row["gols_adv"]) and res_br > res_adv) or (int(row["gols_br"]) < int(row["gols_adv"]) and res_br < res_adv) or (int(row["gols_br"]) == int(row["gols_adv"]) and res_br == res_adv):
                            pt = 10
                        
                        requests.patch(f"{URL}/{row['id']}", headers=HEADERS, json={"fields": {"pontos": str(pt), "acertou_placar_exato": str(exato)}})
                
                if len(acertadores_exato) != 1:
                    for idx, row in df_calculo.iterrows():
                        if row["jogo"] == st.session_state.jogo_atual["confronto"] and row["jogador_atribuido"] == autor_gol:
                            requests.patch(f"{URL}/{row['id']}", headers=HEADERS, json={"fields": {"ganhou_pelo_jogador": "True"}})
                st.success("🏆 Pontuações gravadas!")
                st.rerun()
            
        if st.button("🚨 Resetar Todo o Aplicativo"):
            df_limpo = ler_dados()
            for idx, row in df_limpo.iterrows():
                requests.delete(f"{URL}/{row['id']}", headers=HEADERS)
            st.session_state.jogo_atual["status_finalizado"] = False
            st.rerun()
