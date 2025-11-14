import requests
import streamlit as st
import pandas as pd
import plotly.express as px

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

#team_images = {"Boston College": "WebDevLab03/images/bostoncollege.jpg", "UC Berkeley": "WebDevLab03/images/cal.jpg",
               "Clemson": "WebDevLab03/images/clemson.jpg", "Duke": "WebDevLab03/images/duke.jpg",
               "Florida State": "WebDevLab03/images/fsu.jpg", "Georgia Tech": "WebDevLab03/images/gt.jpg",
               "Louisville": "WebDevLab03/images/louisville.jpg", "University of Miami": "WebDevLab03/images/miami.jpg",
               "NC State": "WebDevLab03/images/ncstate.jpg", "Notre Dame": "WebDevLab03/images/notredame.jpg",
               "University of Pittsburgh": "WebDevLab03/images/pitt.jpg", "SMU": "WebDevLab03/images/smu.jpg",
               "Stanford": "WebDevLab03/images/standford.jpg", "Syracuse": "WebDevLab03/images/syracuse.jpg",
               "UNC": "WebDevLab03/images/unc.jpg", "UVA": "WebDevLab03/images/uva.jpg", "Virginia Tech": "WebDevLab03/images/vt.jpg",
               "Wake Forest": "WebDevLab03/images/wakeforest.jpg"}


import os
st.subheader("DEBUG - Files in images folder:")
st.write("Files in images folder:", os.listdir("WebDevLab03/images"))

selected_team = st.selectbox("Choose an ACC Team:", acc_teams)
season = st.slider("Select Season", 2018, 2025, 2024)
st.image(r"C:\Users\jb100\OneDrive\Documents\WebDevLab03\images\bostoncollege.jpg", width=250, caption=selected_team)

#if selected_team in team_images:
   # st.image(team_images[selected_team], width=250, caption=selected_team)

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
    




