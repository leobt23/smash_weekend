class Team:
    def __init__(self, team_name, players):
        self.team_name = team_name
        self.players = players
        self.top_seeded = False

    def set_top_seeded(self, is_top_seeded):
        self.top_seeded = is_top_seeded


if __name__ == "__main__":
    import psycopg2
    import pandas as pd
    import streamlit as st
    from datetime import datetime
    import plotly.figure_factory as ff  # para o bracket
    import plotly.graph_objects as go

    # ----------------- Função genérica de queries -----------------
    def run_query(query):
        db_connection = psycopg2.connect(
            host="localhost",
            dbname="postgres",
            user="postgres",
            password="1234",
            port="5432",
        )
        cursor = db_connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        cursor.close()
        db_connection.close()
        return pd.DataFrame(rows, columns=colnames)

    # ----------------- FRONTEND -----------------
    # add new logo to the tab
    st.set_page_config(
        page_title="Smash Weekend",
        page_icon="kpadel.png",
        layout="wide"
    )
    # center align title
    st.title("🎾 Smash Weekend - Torneio de Padel")

    tab1, tab2 = st.tabs(["📊 Fase de Grupos", "🏆 Eliminatórias"])  

    # ----------------- TAB 1 - FASE DE GRUPOS -----------------
    with tab1:
        st.header("Classificação por Grupos")

        groups_df = run_query("""
            SELECT g.group_name, t.team_name, gt.points, gt.sets_won
            FROM group_teams gt
            JOIN groups g ON gt.group_id = g.group_id
            JOIN teams t ON gt.team_id = t.team_id
            ORDER BY g.group_name, gt.points DESC, gt.sets_won DESC;
        """)

        group_names = groups_df["group_name"].unique()

        if len(group_names) > 0:
            cols = st.columns(len(group_names))
            for i, g in enumerate(group_names):
                with cols[i]:
                    st.subheader(f"Grupo {g}")
                    df_group = groups_df[groups_df["group_name"] == g].copy()

                    df_group[["player1", "player2"]] = df_group["team_name"].str.split(" / ", expand=True)
                    
                    # Criar HTML da tabela
                    table_html = "<table style='width:100%; border-collapse: collapse;'>"
                    table_html += "<tr><th>Jogador 1</th><th>Jogador 2</th><th>Pontos</th><th>Sets Ganhos</th></tr>"
                    for _, row in df_group.iterrows():
                        table_html += f"<tr><td>{row['player1']}</td><td>{row['player2']}</td><td>{row['points']}</td><td>{row['sets_won']}</td></tr>"
                    table_html += "</table>"

                    st.markdown(table_html, unsafe_allow_html=True)



        else:
            st.info("Ainda não existem grupos registados.")


        st.divider()

        st.subheader("Jogos Realizados")
        played_df = run_query("""
            SELECT g.group_name, m.match_time,
                t1.team_name AS team1, t2.team_name AS team2,
                m.set1_team1, m.set1_team2, m.set2_team1, m.set2_team2, 
                m.super_tiebreak_team1, m.super_tiebreak_team2
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN groups g ON m.group_id = g.group_id
            WHERE m.match_status = 'finished'
            ORDER BY m.match_time ASC;
        """)

        # Converter data/hora
        played_df["match_time"] = pd.to_datetime(played_df["match_time"]).dt.strftime("%d-%m às %H:%M")

        # Criar colunas de sets concatenados
        played_df["Set 1"] = played_df["set1_team1"].astype(str) + "-" + played_df["set1_team2"].astype(str)
        played_df["Set 2"] = played_df["set2_team1"].astype(str) + "-" + played_df["set2_team2"].astype(str)

        # Super tie-break (só se existir)
        played_df["Super Tie-break"] = played_df.apply(
            lambda row: f"{row['super_tiebreak_team1']}-{row['super_tiebreak_team2']}"
            if pd.notnull(row["super_tiebreak_team1"]) else "",
            axis=1
        )

        # Determinar o vencedor de cada jogo
        def get_winner(row):
            # Contagem de sets ganhos
            sets_team1 = 0
            sets_team2 = 0
            for s1, s2 in [(row["set1_team1"], row["set1_team2"]), (row["set2_team1"], row["set2_team2"])]:
                if s1 > s2:
                    sets_team1 += 1
                elif s2 > s1:
                    sets_team2 += 1
            # Super tie-break decide em caso de empate
            if sets_team1 == sets_team2:
                if pd.notnull(row["super_tiebreak_team1"]) and row["super_tiebreak_team1"] != row["super_tiebreak_team2"]:
                    if row["super_tiebreak_team1"] > row["super_tiebreak_team2"]:
                        sets_team1 += 1
                    else:
                        sets_team2 += 1
            return "team1" if sets_team1 > sets_team2 else "team2"

        played_df["winner"] = played_df.apply(get_winner, axis=1)

        # Renomear colunas principais
        played_df = played_df.rename(columns={
            "group_name": "Grupo",
            "match_time": "Data/Hora",
            "team1": "Equipa 1",
            "team2": "Equipa 2"
        })

        # Estilo: verde claro para vencedora, vermelho claro para perdedora
        def highlight_winner(row):
            styles = [""] * len(row)
            if row["winner"] == "team1":
                styles[row.index.get_loc("Equipa 1")] = "background-color: lightgreen"
                styles[row.index.get_loc("Equipa 2")] = "background-color: lightcoral"
            else:
                styles[row.index.get_loc("Equipa 1")] = "background-color: lightcoral"
                styles[row.index.get_loc("Equipa 2")] = "background-color: lightgreen"
            return styles

        # Guardar a informação do vencedor antes de remover colunas
        winner_info = played_df["winner"].copy()

        # Remover colunas que não devem aparecer na tabela final
        played_df = played_df.drop(columns=[
            "set1_team1", "set1_team2", "set2_team1", "set2_team2",
            "super_tiebreak_team1", "super_tiebreak_team2", "winner"
        ])

        # Criar função de estilo que usa a informação guardada do vencedor
        def highlight_winner_final(row):
            styles = [""] * len(row)
            winner = winner_info.iloc[row.name]
            
            if winner == "team1":
                styles[row.index.get_loc("Equipa 1")] = "background-color: lightgreen"
                styles[row.index.get_loc("Equipa 2")] = "background-color: lightcoral"
            else:
                styles[row.index.get_loc("Equipa 1")] = "background-color: lightcoral"
                styles[row.index.get_loc("Equipa 2")] = "background-color: lightgreen"
            return styles

        # Aplicar o estilo no DataFrame final (sem a coluna winner, mas com cores)
        styled_df = played_df.style.apply(highlight_winner_final, axis=1)

        st.dataframe(styled_df, use_container_width=True, hide_index=True)



        st.subheader("Próximos Jogos")
        next_df = run_query("""
            SELECT g.group_name, m.match_time, m.match_location,
                t1.team_name AS team1, t2.team_name AS team2
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN groups g ON m.group_id = g.group_id
            WHERE m.match_status = 'scheduled'
            ORDER BY m.match_time ASC;
        """)

        next_df["match_time"] = pd.to_datetime(next_df["match_time"]).dt.strftime("%d-%m às %H:%M")

        # Renomear colunas
        next_df = next_df.rename(columns={
            "group_name": "Grupo",
            "match_time": "Data/Hora",
            "match_location": "Campo",
            "team1": "Equipa 1",
            "team2": "Equipa 2"
        })

        st.dataframe(next_df, use_container_width=True)



# ----------------- TAB 2 - ELIMINATÓRIAS -----------------

# ----------------- TAB 2 - ELIMINATÓRIAS -----------------
    with tab2:
        st.header("🏆 Eliminatórias do Torneio")
        
        # CSS para o chaveamento visual
        bracket_css = """
        <style>
        .chaveamento {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 60px;
            padding: 30px;
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border-radius: 20px;
            margin: 30px 0;
            overflow-x: auto;
        }
        .ronda {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 30px;
        }
        .titulo-ronda {
            color: white;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 20px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .jogo-card {
            background: white;
            border: 3px solid #34495e;
            border-radius: 15px;
            padding: 20px;
            min-width: 220px;
            max-width: 240px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            position: relative;
        }
        .jogo-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.4);
        }
        .jogo-agendado {
            border-color: #f39c12;
            background: linear-gradient(135deg, #fff 0%, #fef9e7 100%);
        }
        .equipa {
            padding: 12px 10px;
            margin: 8px 0;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        .equipa1 { 
            background-color: #3498db; 
            color: white; 
        }
        .equipa2 { 
            background-color: #e74c3c; 
            color: white; 
        }
        .vs {
            color: #7f8c8d;
            font-weight: bold;
            margin: 10px 0;
            font-size: 16px;
        }
        .placeholder {
            color: #95a5a6;
            font-style: italic;
            font-size: 13px;
            background-color: #ecf0f1 !important;
            color: #7f8c8d !important;
        }
        .final-card {
            border: 4px solid #f39c12 !important;
            background: linear-gradient(135deg, #fff 0%, #fff3cd 100%) !important;
            min-width: 260px;
        }
        .ligacao {
            width: 40px;
            height: 3px;
            background-color: white;
            margin: 0 20px;
            align-self: center;
            border-radius: 2px;
        }
        .match-id {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 12px;
            font-size: 16px;
        }
        .info-text {
            font-size: 11px;
            color: #7f8c8d;
            margin-top: 8px;
            font-style: italic;
        }
        </style>
        """
        
        # Informação explicativa
        st.info("""
        🏆 **Como funcionam as eliminatórias:**
        
        **Quartos de Final:**
        - Os 1ºs classificados de cada grupo jogam contra os 2ºs classificados de outros grupos
        - Sistema de cruzamento: A vs B e C vs D
        
        **Meias-Finais:**
        - Os vencedores dos quartos são emparelhados
        - QF-1 vs QF-3 e QF-2 vs QF-4
        
        **Final:**
        - Os dois vencedores das meias-finais disputam o título
        """)
        
        # Calendário das eliminatórias
        st.subheader("📅 Calendário das Eliminatórias")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏆 Quartos de Final - Sábado**")
            st.write("• QF-1: 10h00 - Pizzaria Papo Seco")
            st.write("• QF-2: 10h00 - Velmar") 
            st.write("• QF-3: 11h00 - Pizzaria Papo Seco")
            st.write("• QF-4: 11h00 - Velmar")
        
        with col2:
            st.write("**🥇 Meias-Finais e Final - Sábado**")
            st.write("• MF-1: 16h00 - Pizzaria Papo Seco")
            st.write("• MF-2: 16h00 - Velmar")
            st.write("• 9º/10º: 17h00 - Pizzaria Papo Seco")
            st.write("• 11º/12º: 17h00 - Velmar")
            st.write("• 3º/4º: 18h15 - Pizzaria Papo Seco")
            st.write("• **FINAL: 19h15 - Pizzaria Papo Seco** 🏆")
        
        # Nota importante
        st.warning("""
        ⚠️ **Nota:** As equipas que avançam para as eliminatórias serão determinadas automaticamente 
        após o término da fase de grupos. Os emparelhamentos seguem o regulamento oficial do torneio.
        """)