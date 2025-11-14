import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="College Football Analysis", page_icon="📊")
st.title("College Football Analysis")

api_key= "PrHYa4qdbOdEVX33hy5RIHnnFqMQLprwVCrw/Oq7Kc1gr00KPF3QJxFwJYKXBL6c"
base_url= "https://api.collegefootballdata.com"
headers = {"Authorization": f"Bearer {api_key}"}

conference = "ACC"

@st.cache_data
def get_teams():
    url = f"{base_url}/teams/fbs?conference={conference}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return sorted([team['school'] for team in response.json()])
    return []

teams = get_teams()

st.header("Team Player Count Comparison")
select_teams = st.multiselect("Select Teams to Comapre (Player Counts)", teams, default = [])

@st.cache_data
def get_roster(team):
    url=f"{base_url}/roster?team={team}&year=2024"
    r=requests.get(url, headers=headers)
    if r.status_code == 200:
        return pd.DataFrame(r.json())
    return pd.DataFrame

player_counts = []
for team in select_teams:
    df= get_roster(team)
    player_counts.append({"Team": team, "Players": len(df)})

if player_counts:
    df_counts = pd.DataFrame(player_counts)
    st.subheader("Team Player Counts (2024)")
    fig_counts = px.bar(df_counts, x="Team", y="Players",
                        title="Number of Players per Team (ACC 2024)")
    st.plotly_chart(fig_counts, use_container_width=True)

acc_teams = ["Boston College", "UC Berkeley", "Clemson", "Duke", "Florida State",
             "Georgia Tech", "Louisville", "University of Miami", "NC State", "Notre Dame",
             "University of Pittsburgh", "SMU", "Stanford", "Syracuse", "UNC", "UVA",
             "Virginia Tech", "Wake Forest"]
import os

IMAGE_DIR = os.path.join("WebDevLab03", "images")

team_images = {
    "Boston College": os.path.join(IMAGE_DIR, "bostoncollege.jpg"),
    "UC Berkeley": os.path.join(IMAGE_DIR, "cal.jpg"),
    "Clemson": os.path.join(IMAGE_DIR, "clemson.jpg"),
    "Duke": os.path.join(IMAGE_DIR, "duke.jpg"),
    "Florida State": os.path.join(IMAGE_DIR, "fsu.jpg"),
    "Georgia Tech": os.path.join(IMAGE_DIR, "gt.jpg"),
    "Louisville": os.path.join(IMAGE_DIR, "louisvilles.jpg"),
    "University of Miami": os.path.join(IMAGE_DIR, "miami.jpg"),
    "NC State": os.path.join(IMAGE_DIR, "ncstate.jpg"),
    "Notre Dame": os.path.join(IMAGE_DIR, "notredame.jpg"),
    "University of Pittsburgh": os.path.join(IMAGE_DIR, "pitt.jpg"),
    "SMU": os.path.join(IMAGE_DIR, "smu.jpg"),
    "Stanford": os.path.join(IMAGE_DIR, "standford.jpg"),
    "Syracuse": os.path.join(IMAGE_DIR, "syracuse.jpg"),
    "UNC": os.path.join(IMAGE_DIR, "unc.jpg"),
    "UVA": os.path.join(IMAGE_DIR, "uva.jpg"),
    "Virginia Tech": os.path.join(IMAGE_DIR, "vt.jpg"),
    "Wake Forest": os.path.join(IMAGE_DIR, "wakeforest.jpg"),
}


selected_team = st.selectbox("Choose an ACC Team:", acc_teams)
season = st.slider("Select Season", 2018, 2025, 2024)

if selected_team in team_images:
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/jpeg;base64,{base64.b64encode(open(team_images[selected_team], 'rb').read()).decode()}" width="300">
            <p><strong>{selected_team}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    

@st.cache_data
def get_team_stats(team, year):
    url = f"{base_url}/stats/season?year={year}&team={team}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Error fetching stats: {r.status_code}")
        st.text(r.text)
        return []
    if not r.text.strip():
        st.warning("No data returned from API.")
        return []
    try:
        return r.json()
    except ValueError:
        st.error("Invalid JSON received from API.")
        st.text(r.text[:500])
        return []
        

data = get_team_stats(selected_team, season)

if data:
    df = pd.DataFrame(data)
    df = df[["statName", "statValue"]]
    df.rename(columns = {"statName": "Stat", "statValue": "Value"}, inplace=True)
    st.subheader(f"{selected_team} Team Stats ({season})")
    st.dataframe(df)
    fig = px.bar(df, x="Stat", y="Value", title=f"{selected_team} Team Statistics ({season})")
    st.plotly_chart(fig, use_container_width=True)


st.header("Player Filter")

position = st.selectbox("Select Player Position", ["QB", "RB", "WR", "TE",])

@st.cache_data
def get_player_stats(year, team):
    url = f"{base_url}/stats/player/season?year={year}&team={team}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return pd.DataFrame(r.json())
    return pd.DataFrame()

player_df = get_player_stats(season, selected_team)

if not player_df.empty:
    filtered = player_df[player_df["position"] == position]
    st.subheader(f"{selected_team} {position}s in {season}")
    show_cols = [c for c in ["player", "category", "statType", "stat"] if c in filtered.columns]
    st.dataframe(filtered[show_cols])

    if st.checkbox("Show Stat Distribution"):
        agg = filtered.groupby("category")["stat"].sum().reset_index()
        fig2 = px.bar(agg, x="category", y="stat", title= f"{position} Stats Breakdown")
        st.plotly_chart(fig2, use_container_width = True)
    else:
        st.warning("No player data found for this selection")
    









