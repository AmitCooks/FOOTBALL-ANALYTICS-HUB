"""
app.py
Football Player Performance Analytics Dashboard — Entry Point
Synthetic data · for demonstration only
"""

import pandas as pd
import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Football Analytics Hub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS — dark football theme ─────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── App background ── */
    .stApp {
        background-color: #0e1117;
        color: #f0f2f6;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #161b27;
        border-right: 1px solid #2a3245;
    }
    [data-testid="stSidebar"] * {
        color: #f0f2f6 !important;
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background-color: #1c2330;
        border: 1px solid #2a3245;
        border-radius: 10px;
        padding: 16px 20px;
    }
    [data-testid="metric-container"] label {
        color: #8b9ab5 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #00b359 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* ── Headings ── */
    h1, h2, h3 { color: #f0f2f6 !important; }

    /* ── DataFrames ── */
    [data-testid="stDataFrame"] {
        border: 1px solid #2a3245;
        border-radius: 8px;
    }

    /* ── Buttons ── */
    .stDownloadButton > button, .stButton > button {
        background-color: #00b359 !important;
        color: #0e1117 !important;
        font-weight: 700;
        border: none;
        border-radius: 6px;
    }
    .stDownloadButton > button:hover, .stButton > button:hover {
        background-color: #00cc66 !important;
    }

    /* ── Multiselect tags ── */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #00b359 !important;
        color: #0e1117 !important;
    }

    /* ── Divider ── */
    hr { border-color: #2a3245; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv("football_players.csv")


df_all = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ Football Analytics Hub")
    st.markdown("---")

    # Season filter
    all_seasons = sorted(df_all["season"].unique())
    selected_seasons = st.multiselect(
        "📅 Season",
        options=all_seasons,
        default=all_seasons,
    )
    df_s = df_all[df_all["season"].isin(selected_seasons)] if selected_seasons else df_all

    # Team filter (options narrowed by season)
    all_teams = sorted(df_s["team"].unique())
    selected_teams = st.multiselect(
        "🏟️ Team",
        options=all_teams,
        default=all_teams,
    )
    df_t = df_s[df_s["team"].isin(selected_teams)] if selected_teams else df_s

    # Position filter (options narrowed by season + team)
    all_positions = sorted(df_t["position"].unique())
    selected_positions = st.multiselect(
        "🎽 Position",
        options=all_positions,
        default=all_positions,
    )
    df_p = df_t[df_t["position"].isin(selected_positions)] if selected_positions else df_t

    # Player filter (options narrowed by all above)
    all_players = sorted(df_p["player_name"].unique())
    selected_players = st.multiselect(
        "👤 Player",
        options=all_players,
        placeholder="All players",
    )
    filtered_df = (
        df_p[df_p["player_name"].isin(selected_players)]
        if selected_players
        else df_p
    )

    st.markdown("---")
    st.caption("⚠️ Synthetic data · for demonstration only")

# ── Validation ────────────────────────────────────────────────────────────────
if filtered_df.empty:
    st.warning("⚠️ No players match the current filters. Please broaden your selection.")
    st.stop()

# ── Store in session_state for all pages ─────────────────────────────────────
st.session_state["filtered_df"] = filtered_df

# ── Home splash (visible on the root app.py page) ────────────────────────────
st.markdown("# ⚽ Football Analytics Hub")
st.markdown(
    "Use the **sidebar** to filter by season, team, position, or player, "
    "then navigate to any page using the menu on the left."
)
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.info("📊 **Overview** — KPI cards & leaderboard")
with col2:
    st.info("🔍 **Player Analysis** — Compare players & scatter plots")
with col3:
    st.info("🏟️ **Team Analysis** — Team-level goals & assists")
with col4:
    st.info("🎽 **Position Analysis** — Stats by position")
