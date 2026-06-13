import streamlit as st
import random, pandas as pd, requests

st.set_page_config(page_title="Bolão Brasil 2026", layout="centered")
st.markdown("<style>.stTabs [aria-selected='true'] {background-color: #009c3b !important; color: #ffdf00 !important; font-weight: bold;} div[data-testid='stHeader'] {background-color: #009c3b;}</style>", unsafe_allow_html=True)

try:
    URL = f"https://airtable.com{st.secrets['airtable']['base_id'].strip()}/{st.secrets['airtable']['table_id'].strip()}"
    HEADERS = {"Authorization": f"Bearer {st.secrets['airtable']['token'].strip()}", "Content-Type": "application/json"}
except:
    st.error("❌ Configure os Secrets no Streamlit!")
    st.stop()

def ler_dados():
    res = requests.get(URL, headers=HEADERS, timeout=10)
    if res.status_code == 200:
        records = res.json().get("records", [])
        if not records: return pd.DataFrame(columns=["id","jogo","nome","gols_br","gols_adv","jogador_atribuido","pontos","acertou_placar_exato","ganhou_pelo_jogador"])
        df = pd.DataFrame([dict(r.get("fields", {}), id=r.get("id")) for r in records])
        for col in ["gols_br", "gols_adv", "pontos"]: df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0).astype(int)
        return df
    return pd.DataFrame(columns=["id","jogo","nome","gols_br","gols_adv","jogador_atribuido","pontos","acertou_placar_exato","ganhou_pelo_jogador"])

JOGOS = {"1ª Rodada: Brasil x Marrocos": "Brasil x Marrocos", "2ª Rodada: Brasil x Haiti": "Brasil x Haiti", "3ª Rodada: Escócia x Brasil": "Escócia x Brasil", "Fase Customizada (Mata-Mata)": "Brasil x Adversário"}
if "jg_ch" not in st.session_state: st.session_state.jg_ch = "1ª Rodada: Brasil x Marrocos"
if "jg_at" not in st.session_state: st.session_state.jg_at = {"confronto": JOGOS[st.session_state.jg_ch], "placar_real_br": 0, "placar_real_adv": 0, "autor_ultimo_gol": "Ninguém", "status_finalizado": False}

JOGADORES = ["Alex Sandro", "Bremer", "Danilo", "Douglas Santos", "Gabriel Magalhães", "Ibañez", "Léo Pereira", "Marquinhos", "Wesley", "Bruno Guimarães", "Casemiro", "Danilo (Botafogo)", "Fabinho", "Lucas Paquetá", "Endrick", "Gabriel Martinelli", "Igor Thiago", "Luiz Henrique", "Matheus Cunha", "Neymar", "Raphinha", "Rayan", "Vini Jr."]

aba_palpites, aba_ranking, aba_admin = st.tabs(["📝 DAR PALPITE", "📊 CLASSIFICAÇÃO", "🔒 ADMINISTRADOR"])

with aba_palpites:
    st.markdown("<h1 style='text-align: center; color: #009c3b;'>🇧🇷 Bolão Copa 2026 🇧🇷</h1>", unsafe_allow_html=True)
    st.subheader(f"Partida Ativa: {st.session_state.jg_at['confronto']}")
    if st.session_state.jg_at["status_finalizado"]:
        st.warning("⚠️ Os palpites para este jogo já estão encerrados.")
    else:
        with st.form(key="cad_palpite", clear_on_submit=True):
            nome = st.text_input("Seu Nome:")
            col1, col2 = st.columns(2)
            g_br = col1.number_input("Gols do Brasil:", min_value=0, step=1)
            g_adv = col2.number_input("Gols do Adversário:", min_value=0, step=1)
            if st.form_submit_button("🚀 ENVIAR PALPITE") and nome.strip():
                nl = nome.strip().title()
                df = ler_dados()
                if not df.empty and "jogo" in df.columns and ((df["nome"] == nl) & (df["jogo"] == st.session_state.jg_at["confronto"])).any():
                    st.error("❌ Você já cadastrou palpite para este jogo!")
                else:
                    sorteado = random.choice(JOGADORES)
                    payload = {"records": [{"fields": {"jogo": st.session_state.jg_at["confronto"], "nome": nl, "gols_br": int(g_br), "gols_adv": int(g_adv), "jogador_atribuido": sorteado, "pontos": 0, "acertou_placar_exato": "False", "ganhou_pelo_jogador": "False"}}]}
                    res = requests.post(URL, headers=HEADERS, json=payload, timeout=10)
                    if res.status_code == 200:
                        st.balloons(); st.success(f"✅ {nl}! Seu jogador da sorte é: {sorteado}")
                    else:
                        st.error(f"❌ Erro na tabela do Airtable (Código {res.status_code}). Verifique as colunas.")

with aba_ranking:
    st.markdown("<h2 style='color: #009c3b;'>🏆 Classificação Geral e Resultados</h2>", unsafe_allow_html=True)
    if st.session_state.jg_at["status_finalizado"]:
        st.info(f"Placar Oficial: {st.session_state.jg_at['confronto']} ({st.session_state.jg_at['placar_real_br']}x{st.session_state.jg_at['placar_real_adv']}) | Último gol: {st.session_state.jg_at['autor_ultimo_gol']}")
    df_n = ler_dados()
    if not df_n.empty and "jogo" in df_n.columns:
        df_f = df_n[df_n["jogo"] == st.session_state.jg_at["confronto"]]
        if not df_f.empty:
            st.markdown("#### ⚽ Palpites da Rodada Ativa")
            st.dataframe(df_f[["nome", "gols_br", "gols_adv", "jogador_atribuido", "pontos"]].sort_values(by="pontos", ascending=False), use_container_width=True)
        st.markdown("#### 📈 CLASSIFICAÇÃO GERAL DO TORNEIO (Acumulado)")
        df_g = df_n.groupby("nome")["pontos"].sum().reset_index().sort_values(by="pontos", ascending=False)
        df_g.columns = ["Nome do Participante", "Pontos Totais Acumulados"]
        st.dataframe(df_g, use_container_width=True)
    else: st.write("Nenhum palpite cadastrado.")

with aba_admin:
    st.header("🔒 Painel do Organizador")
    if st.text_input("Senha de administrador:", type="password") == "brasil2026":
        st.success("Acesso autorizado!")
        esc = st.selectbox("Ativar qual jogo?", list(JOGOS.keys()), index=list(JOGOS.keys()).index(st.session_state.jg_ch))
        conf_f = JOGOS[esc] if esc != "Fase Customizada (Mata-Mata)" else st.text_input("Digite o confronto:", value="Brasil x ")
        if st.button("Confirmar Mudança de Jogo"):
            st.session_state.jg_ch = esc; st.session_state.jg_at = {"confronto": conf_f, "placar_real_br": 0, "placar_real_adv": 0, "autor_ultimo_gol": "Ninguém", "status_finalizado": False}
            st.rerun()
        st.markdown("---")
        res_br = st.number_input("Gols REAIS do Brasil:", min_value=0, step=1)
        res_adv = st.number_input("Gols REAIS do Adversário:", min_value=0, step=1)
        aut = st.selectbox("Último gol do Brasil:", ["Ninguém"] + JOGADORES)
        if st.button("🔴 Fechar Rodada e Computar Pontos"):
            st.session_state.jg_at.update({"placar_real_br": res_br, "placar_real_adv": res_adv, "autor_ultimo_gol": aut, "status_finalizado": True})
            df_c = ler_dados()
            if not df_c.empty:
                ac_ex = []
                for idx, r in df_c.iterrows():
                    if r["jogo"] == st.session_state.jg_at["confronto"]:
                        ex = (int(r["gols_br"]) == res_br and int(r["gols_adv"]) == res_adv)
                        pt = 25 if ex else (18 if (int(r["gols_br"])-int(r["gols_adv"])) == (res_br-res_adv) and (int(r["gols_br"]) != int(r["gols_adv"])) else (10 if (int(r["gols_br"])>int(r["gols_adv"]) and res_br>res_adv) or (int(r["gols_br"])<int(r["gols_adv"]) and res_br<res_adv) or (int(r["gols_br"])==int(r["gols_adv"]) and res_br==res_adv) else 0))
                        if ex: ac_ex.append(r["id"])
                        requests.patch(f"{URL}/{r['id']}", headers=HEADERS, json={"fields": {"pontos": pt, "acertou_placar_exato": str(ex)}})
                if len(ac_ex) != 1:
                    for idx, r in df_c.iterrows():
                        if r["jogo"] == st.session_state.jg_at["confronto"] and r["jogador_atribuido"] == aut:
                            requests.patch(f"{URL}/{r['id']}", headers=HEADERS, json={"fields": {"ganhou_pelo_jogador": "True"}})
                st.success("🏆 Pontuações gravadas!"); st.rerun()
        if st.button("🚨 Resetar Todo o Aplicativo"):
            for idx, r in ler_dados().iterrows(): requests.delete(f"{URL}/{r['id']}", headers=HEADERS)
            st.session_state.jg_at["status_finalizado"] = False; st.rerun()
