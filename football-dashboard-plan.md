# Football Player Performance Analytics Dashboard — Implementation Plan

## Top-Level Overview

Build a portfolio-quality, interactive football (soccer) analytics dashboard using Python, Streamlit,
Pandas, NumPy, and Plotly. The project is greenfield (empty workspace). All data is synthetic and
clearly labelled as such. The UI follows a dark, modern, football-inspired green-pitch theme.

**Scope:**
- 4 deliverables: `app.py`, `football_players.csv`, `requirements.txt`, `README.md`
- Multi-page Streamlit app (`pages/` folder) with a shared sidebar
- Synthetic dataset: 100+ players, 8 fictional clubs, 3 seasons, 4 positions
- All KPIs and rankings calculated from the dataset — nothing hardcoded

**Out of scope:**
- Real-world / live data feeds
- User authentication
- Radar / spider charts
- External APIs

---

## Dataset Schema

File: `football_players.csv`

| Column | Type | Description |
|---|---|---|
| `player_id` | int | Unique identifier |
| `player_name` | str | Full name |
| `team` | str | One of 8 fictional club names |
| `position` | str | GK / DEF / MID / FWD |
| `season` | str | 2022/23 · 2023/24 · 2024/25 |
| `age` | int | 18–36 |
| `matches_played` | int | 1–38 |
| `minutes_played` | int | matches_played × ~70–90 |
| `goals` | int | Position-weighted random int |
| `assists` | int | Position-weighted random int |
| `shots` | int | goals-correlated random int |
| `pass_accuracy` | float | 60–95 % |
| `dribbles` | int | 0–80 |
| `yellow_cards` | int | 0–10 |
| `red_cards` | int | 0–3 |
| `rating` | float | 5.0–9.5 (composite, not hardcoded) |

**Generation rules:**
- Use `numpy.random.seed(42)` for full reproducibility
- Position-based stat weighting: FWD highest goals/shots, GK lowest; MID highest assists/pass_accuracy
- `rating` derived as a weighted formula across goals, assists, pass_accuracy, and minutes
- Dataset labelled with a `data_note` constant in the code: *"Synthetic data — for demonstration only"*

---

## KPI Calculations

All computed at runtime from filtered DataFrame:

| KPI | Formula |
|---|---|
| Total Players | `df['player_id'].nunique()` |
| Total Goals | `df['goals'].sum()` |
| Total Assists | `df['assists'].sum()` |
| Total Minutes Played | `df['minutes_played'].sum()` |
| Average Rating | `df['rating'].mean()` rounded to 2 dp |
| Top 10 Players | Sort by `goals` desc, then `rating` desc — take head 10 |

---

## Project Structure

```
football-analytics-hub/
├── app.py                   # Entry point — sets page config, theme, sidebar filters
├── football_players.csv     # Synthetic dataset (generated once by data_generator.py)
├── data_generator.py        # Standalone script to regenerate the CSV
├── requirements.txt
├── README.md
└── pages/
    ├── 1_Overview.py        # KPI cards + Top 10 leaderboard
    ├── 2_Player_Analysis.py # Player comparison + scatter plots
    ├── 3_Team_Analysis.py   # Team-level bar charts
    └── 4_Position_Analysis.py  # Position breakdown charts
```

---

## UI Theme

- Background: `#0e1117` (near-black)
- Accent / pitch green: `#00b359`
- Card background: `#1c2330`
- Text: `#f0f2f6`
- Applied via `st.markdown` CSS injection in `app.py`
- Plotly charts use `plotly_dark` template with green accent colours

---

## Sub-Tasks

---

### Sub-Task 1 — Synthetic Dataset & Data Generator

**Intent:** Create the reproducible CSV and the standalone generator script so every other sub-task
has real data to work with.

**Expected Outcomes:**
- `data_generator.py` exists and runs with `python data_generator.py`
- `football_players.csv` is produced with ≥ 100 rows, correct schema, no nulls
- Columns match the schema table above exactly
- Stats are position-weighted (FWD scores more goals than GK)

**Todo List:**
1. Create `data_generator.py` with `numpy.random.seed(42)`
2. Define the 8 club names and 4 positions with their stat weights
3. Generate ~120 player rows × 3 seasons = ~360 rows total
4. Compute `rating` as a weighted formula (not a raw random number)
5. Save to `football_players.csv`
6. Print a confirmation summary (row count, column list)

**Relevant Context:**
- Schema table above
- `rating` formula: `0.4*(goals/max_goals) + 0.3*(assists/max_assists) + 0.2*(pass_accuracy/100) + 0.1*(minutes_played/max_minutes)` scaled to 5–9.5 (attack-focused weighting)
- No external dependencies beyond `pandas` and `numpy`

**Status:** `[x] done`

---

### Sub-Task 2 — App Entry Point, Theme & Shared Sidebar

**Intent:** Build `app.py` as the Streamlit entry point that sets the global page config, injects the
dark green CSS theme, loads the CSV, applies sidebar filters, and exposes a filtered DataFrame that
all pages can consume via `st.session_state`.

**Expected Outcomes:**
- `streamlit run app.py` launches without error and shows the sidebar
- Sidebar contains: Season (multiselect), Team (multiselect), Position (multiselect), Player (multiselect)
- Filtered data is stored in `st.session_state['filtered_df']`
- Theme CSS is applied globally (dark background, green accents)
- A warning message is shown when filters return 0 rows

**Todo List:**
1. Create `app.py` with `st.set_page_config` (title, icon, layout="wide", dark theme)
2. Inject CSS via `st.markdown` for background, card, and accent colours
3. Load `football_players.csv` with `@st.cache_data`
4. Build sidebar with cascading filter widgets (each filter updates the next's options)
5. Validate that filtered DataFrame is non-empty; show `st.warning` if not
6. Store filtered DataFrame in `st.session_state`
7. Show a small "Synthetic Data" disclaimer banner at the bottom of the sidebar

**Relevant Context:**
- Streamlit multi-page apps auto-discover files in `pages/` — `app.py` is the root page
- Cascading filters: Season → Team → Position → Player
- CSS snippet targets `.stApp`, `.css-1d391kg`, metric cards via class selectors

**Status:** `[x] done`

---

### Sub-Task 3 — Overview Page

**Intent:** Build `pages/1_Overview.py` to give a high-level snapshot of the filtered dataset via
KPI cards and a Top 10 leaderboard.

**Expected Outcomes:**
- Five KPI metric cards in a single row: Total Players, Total Goals, Total Assists, Total Minutes Played, Average Rating
- Top 10 Players leaderboard table below the cards (sorted by goals then rating)
- All values respond correctly to sidebar filter changes
- Page shows a friendly error if `session_state['filtered_df']` is missing or empty

**Todo List:**
1. Create `pages/1_Overview.py`
2. Read `st.session_state['filtered_df']`; guard against missing/empty state
3. Calculate the 5 KPIs from the filtered DataFrame
4. Render KPIs using `st.metric` in `st.columns(5)`
5. Build Top 10 table: sort by goals desc, rating desc; select display columns; style with `st.dataframe`
6. Add page title and subtitle with the "Synthetic Data" note

**Relevant Context:**
- `st.metric` supports delta values — show delta vs. unfiltered total if desired (optional)
- Top 10 display columns: Rank, Player Name, Team, Position, Goals, Assists, Rating

**Status:** `[x] done`

---

### Sub-Task 4 — Player Analysis Page

**Intent:** Build `pages/2_Player_Analysis.py` for individual player deep-dives with a side-by-side
comparison widget and two scatter plots.

**Expected Outcomes:**
- Two-player comparison selector (two `st.selectbox` widgets side by side) showing a stat table
- Goals vs Assists scatter plot (all filtered players, selected players highlighted)
- Shots vs Goals scatter plot (all filtered players, sized by minutes played)
- Tooltips show player name, team, position, and relevant stats
- Handles edge cases: fewer than 2 players available in filter

**Todo List:**
1. Create `pages/2_Player_Analysis.py`
2. Read and validate `st.session_state['filtered_df']`
3. Build two-column player selector; show comparison stat table via `st.dataframe`
4. Build Goals vs Assists scatter with `px.scatter`; highlight selected players with a second trace
5. Build Shots vs Goals scatter with `px.scatter`; size marker by `minutes_played`
6. Apply `plotly_dark` template and green accent colour to both charts
7. Add descriptive chart titles and axis labels

**Relevant Context:**
- Use `plotly.graph_objects` overlay trace for highlighted players on top of base scatter
- Colour scale: use `color='position'` for base scatter for instant visual grouping

**Status:** `[x] done`

---

### Sub-Task 5 — Team Analysis Page

**Intent:** Build `pages/3_Team_Analysis.py` to show aggregated team-level performance.

**Expected Outcomes:**
- Grouped bar chart: Total Goals and Total Assists per team
- Bar chart: Player count per team
- Summary table of team stats (goals, assists, avg rating, player count)
- All charts respond to sidebar filters

**Todo List:**
1. Create `pages/3_Team_Analysis.py`
2. Read and validate `st.session_state['filtered_df']`
3. Aggregate by team: sum goals, sum assists, count players, mean rating
4. Build grouped bar chart (goals + assists) with `px.bar` using `barmode='group'`
5. Build player count bar chart
6. Render team summary table with `st.dataframe`

**Relevant Context:**
- Sort teams by total goals descending for consistent ordering
- Use the same green accent palette as other pages

**Status:** `[x] done`

---

### Sub-Task 6 — Position Analysis Page

**Intent:** Build `pages/4_Position_Analysis.py` to break down stats by position (GK / DEF / MID / FWD).

**Expected Outcomes:**
- KPI cards per position (avg goals, avg assists, avg rating)
- Bar chart: Average goals per position
- Bar chart: Average rating per position
- Box plot or violin chart: Rating distribution per position (use `px.box`)

**Todo List:**
1. Create `pages/4_Position_Analysis.py`
2. Read and validate `st.session_state['filtered_df']`
3. Aggregate by position: mean goals, mean assists, mean rating, player count
4. Render one `st.columns(4)` row of KPI cards — one per position
5. Build average goals bar chart
6. Build average rating bar chart
7. Build rating distribution box plot with `px.box`

**Relevant Context:**
- Position order for display: GK → DEF → MID → FWD
- Box plot is more informative than a bar chart for rating spread

**Status:** `[x] done`

---

### Sub-Task 7 — Searchable Stats Table & CSV Download

**Intent:** Add a searchable, filterable player stats table with a CSV download button — this lives
as a section at the bottom of the Overview page (or as a fifth page if preferred).

**Expected Outcomes:**
- Full stats table rendered with `st.dataframe` (with column sorting enabled)
- A text input box for player name search (filters the displayed table only)
- A `st.download_button` that exports the current filtered DataFrame as a CSV
- Download filename includes the active season filter

**Todo List:**
1. Add a "Player Statistics" expander/section to `pages/1_Overview.py` below the Top 10 table
2. Add a `st.text_input` for player name search; apply `.str.contains` filter
3. Display the result table with `st.dataframe(use_container_width=True)`
4. Add `st.download_button` with `df.to_csv(index=False)` and a dynamic filename

**Relevant Context:**
- `st.download_button` requires `data=` as bytes or string — use `df.to_csv(index=False).encode('utf-8')`
- Dynamic filename example: `football_data_2024-25.csv`

**Status:** `[x] done`

---

### Sub-Task 8 — requirements.txt & README

**Intent:** Provide everything needed to run and deploy the app.

**Expected Outcomes:**
- `requirements.txt` lists exact packages: `streamlit`, `pandas`, `numpy`, `plotly`
- `README.md` includes: project overview, dataset note, local run instructions, Streamlit Cloud deploy instructions, and a project structure diagram

**Todo List:**
1. Create `requirements.txt` with pinned or minimum versions
2. Create `README.md` with sections: Overview, Dataset, Project Structure, Run Locally, Deploy to Streamlit Cloud, Screenshots placeholder

**Relevant Context:**
- Streamlit Cloud deploy: push to GitHub → connect repo at share.streamlit.io → set `app.py` as entry point
- No secrets or environment variables required

**Status:** `[x] done`

---

## Implementation Order

Sub-tasks should be executed in this sequence — each depends on the previous:

1. Dataset & Generator (data must exist before any page is built)
2. App Entry Point & Sidebar (shared state must exist before pages read it)
3. Overview Page (first page users see)
4. Player Analysis Page
5. Team Analysis Page
6. Position Analysis Page
7. Stats Table & CSV Download (extends Overview page)
8. requirements.txt & README
