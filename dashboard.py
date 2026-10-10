import os
import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.eda import (
    load_clean_data,
    matches_per_season,
    most_successful_teams,
    toss_impact,
    top_run_scorers,
    top_wicket_takers,
)

# Page configuration
st.set_page_config(page_title="IPL Data Dashboard", page_icon="🏏", layout="wide")

# Custom CSS for aesthetics (Glassmorphism & dark mode tweaks)
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    h1, h2, h3 {
        color: #FF4B4B;
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏏 IPL Data Analytics Dashboard")
st.markdown("An interactive dashboard analyzing IPL data from 2008 onwards.")

# Load Data
@st.cache_data
def fetch_data():
    data_dir = ROOT / 'data'
    try:
        matches, deliveries = load_clean_data(str(data_dir))
        if len(matches) > 0:
            return matches, deliveries
    except Exception:
        pass

    with st.spinner('Extracting match and delivery datasets from your original file... this may take a minute!'):
        from src.data_cleaning import explore_and_clean
        explore_and_clean()

        try:
            matches, deliveries = load_clean_data(str(data_dir))
            if len(matches) > 0:
                return matches, deliveries
        except Exception:
            pass

    return None, None

matches, deliveries = fetch_data()

if matches is None or deliveries is None:
    st.error("Dataset not found! Please run `src/data_cleaning.py` first to generate the cleaned CSV files.")
else:
    # Sidebar
    st.sidebar.header("Filter Options")
    seasons = sorted(matches['season'].dropna().unique().tolist())
    selected_season = st.sidebar.selectbox("Select Season", ["All Time"] + seasons)

    filtered_matches = matches.copy()
    filtered_deliveries = deliveries.copy()

    if selected_season != "All Time":
        filtered_matches = filtered_matches[filtered_matches['season'] == selected_season]
        valid_match_ids = filtered_matches['id'].unique()
        filtered_deliveries = filtered_deliveries[filtered_deliveries['match_id'].isin(valid_match_ids)]
    else:
        filtered_matches = matches.copy()
        filtered_deliveries = deliveries.copy()

    season_data = matches_per_season(filtered_matches) if selected_season == "All Time" else None

    # --- TOP METRICS ROW ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><h3>Total Matches</h3><h2>{len(filtered_matches)}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h3>Total Runs</h3><h2>{filtered_deliveries['total_runs'].sum()}</h2></div>", unsafe_allow_html=True)
    with col3:
        total_wickets = filtered_deliveries['bowler_wicket'].sum() if 'bowler_wicket' in filtered_deliveries.columns else 0
        st.markdown(f"<div class='metric-card'><h3>Total Wickets</h3><h2>{int(total_wickets)}</h2></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><h3>Super Overs</h3><h2>{filtered_matches['is_super_over'].sum() if 'is_super_over' in filtered_matches.columns else 0}</h2></div>", unsafe_allow_html=True)

    # --- CHARTS SECTION ---
    st.markdown("---")
    colA, colB = st.columns(2)

    with colA:
        st.subheader("📊 Matches Played Per Season")
        if season_data is not None:
            fig = px.line(season_data, x='season', y='matches', markers=True,
                          title="Trend of Matches over Seasons",
                          color_discrete_sequence=['#00E5FF'])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"Showing data for season {selected_season}. Select 'All Time' for season trend.")

    with colB:
        st.subheader("🏆 Most Successful Teams")
        team_data = most_successful_teams(filtered_matches).head(10)
        fig2 = px.bar(team_data, x='wins', y='team', orientation='h',
                      title="Total Wins by Team",
                      color='wins', color_continuous_scale="Viridis")
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    colC, colD = st.columns(2)

    with colC:
        st.subheader("🏏 Top Run Scorers")
        runs_data = top_run_scorers(filtered_deliveries, 10)
        if runs_data is not None and not runs_data.empty:
            fig3 = px.bar(runs_data, x='batsman', y='batsman_runs',
                          title="Top 10 Batsmen by Runs",
                          color='batsman_runs', color_continuous_scale="Oranges")
            fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("No run scoring data available for the selected filter.")

    with colD:
        st.subheader("🎯 Top Wicket Takers")
        wickets_data = top_wicket_takers(filtered_deliveries, 10)
        if wickets_data is not None and not wickets_data.empty:
            fig4 = px.bar(wickets_data, x='bowler', y='wickets',
                          title="Top 10 Bowlers by Wickets",
                          color='wickets', color_continuous_scale="Teal")
            fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("No wicket data available for the selected filter.")

    # --- TOSS IMPACT PIE CHART ---
    st.markdown("---")
    st.subheader("🪙 Toss Impact (Does winning Toss = Winning Match?)")
    impact_data = toss_impact(filtered_matches).reset_index()
    impact_data.columns = ['Won Match', 'Percentage']
    impact_data['Won Match'] = impact_data['Won Match'].map({True: 'Yes', False: 'No'})

    fig5 = px.pie(impact_data, values='Percentage', names='Won Match',
                  color='Won Match', color_discrete_map={'Yes': '#00E5FF', 'No': '#FF4B4B'},
                  hole=0.4)
    fig5.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig5, use_container_width=True)

    st.caption("Built for 3rd Year Mini Project | using Streamlit, Plotly, & Pandas")

0