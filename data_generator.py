"""
data_generator.py
Generates a reproducible synthetic football player dataset.
NOTE: All data is synthetic and for demonstration purposes only.
Run: python data_generator.py
"""

import numpy as np
import pandas as pd

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)

DATA_NOTE = "Synthetic data — for demonstration only"

# ── Constants ─────────────────────────────────────────────────────────────────
CLUBS = [
    "FC Dynamo",
    "Athletic United",
    "Riverside City FC",
    "Northern Rangers",
    "Capital SC",
    "Bay City Athletic",
    "Ironclad FC",
    "Eastside Rovers",
]

POSITIONS = ["GK", "DEF", "MID", "FWD"]
SEASONS = ["2022/23", "2023/24", "2024/25"]

# Players per club (squad size ~19 gives ~152 unique players across 8 clubs)
SQUAD_SIZE = 19

# Position weights per club squad slot (GK, DEF, MID, FWD)
POSITION_DIST = ["GK"] * 2 + ["DEF"] * 5 + ["MID"] * 7 + ["FWD"] * 5

# ── Stat weight tables (mean, std) per position ───────────────────────────────
STAT_WEIGHTS = {
    #              goals      assists   shots      pass_acc   dribbles
    "GK":  dict(goals=(0, 0.3),  assists=(0, 0.5),  shots=(0, 0.5),  pass_acc=(72, 6),  dribbles=(1, 1)),
    "DEF": dict(goals=(2, 2),    assists=(3, 2),    shots=(8, 4),    pass_acc=(78, 6),  dribbles=(10, 7)),
    "MID": dict(goals=(5, 4),    assists=(7, 4),    shots=(30, 12),  pass_acc=(84, 5),  dribbles=(35, 15)),
    "FWD": dict(goals=(12, 6),   assists=(5, 3),    shots=(55, 18),  pass_acc=(74, 7),  dribbles=(40, 18)),
}

# ── Helper ────────────────────────────────────────────────────────────────────
def _rand_int(mean, std, low=0, high=None):
    val = int(np.round(np.random.normal(mean, std)))
    val = max(low, val)
    if high is not None:
        val = min(high, val)
    return val


def _rand_float(mean, std, low=0.0, high=None, decimals=1):
    val = round(float(np.random.normal(mean, std)), decimals)
    val = max(low, val)
    if high is not None:
        val = min(high, val)
    return val


# ── First-name / last-name pools ──────────────────────────────────────────────
FIRST_NAMES = [
    "Luca", "Marco", "Carlos", "James", "Emil", "Andre", "Felix", "Oscar",
    "Diego", "Theo", "Noah", "Kai", "Leo", "Max", "Ivan", "Yusuf", "Rafa",
    "Arjan", "Sven", "Nils", "Tomas", "Bram", "Hugo", "Pedro", "Luis",
]
LAST_NAMES = [
    "Silva", "Müller", "García", "Johnson", "Eriksen", "Santos", "Koch",
    "Lindström", "Moreno", "Bouchard", "Kovač", "Nkosi", "Ferreira",
    "Andersen", "Osei", "Tanaka", "Reyes", "Blanc", "Holt", "Fischer",
]


def _make_name(used: set) -> str:
    for _ in range(1000):
        name = f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}"
        if name not in used:
            used.add(name)
            return name
    raise RuntimeError("Name pool exhausted")


# ── Dataset generation ────────────────────────────────────────────────────────
def generate_dataset() -> pd.DataFrame:
    used_names: set = set()
    player_id = 1
    rows = []

    for club in CLUBS:
        # Assign a fixed squad with names persisting across seasons
        squad = []
        for pos in POSITION_DIST:
            squad.append({"name": _make_name(used_names), "position": pos})

        for season in SEASONS:
            for player in squad:
                pos = player["position"]
                w = STAT_WEIGHTS[pos]

                matches = _rand_int(28, 7, low=5, high=38)
                minutes = matches * _rand_int(75, 12, low=30, high=90)
                goals   = _rand_int(*w["goals"],   low=0, high=50)
                assists = _rand_int(*w["assists"],  low=0, high=30)
                shots   = _rand_int(*w["shots"],   low=goals, high=120)
                pass_ac = _rand_float(*w["pass_acc"], low=50.0, high=99.0)
                dribbles = _rand_int(*w["dribbles"], low=0, high=120)
                yellow  = _rand_int(2, 2, low=0, high=10)
                red     = _rand_int(0, 0.4, low=0, high=3)
                age     = _rand_int(24, 4, low=18, high=36)

                rows.append({
                    "player_id":      player_id,
                    "player_name":    player["name"],
                    "team":           club,
                    "position":       pos,
                    "season":         season,
                    "age":            age,
                    "matches_played": matches,
                    "minutes_played": minutes,
                    "goals":          goals,
                    "assists":        assists,
                    "shots":          shots,
                    "pass_accuracy":  pass_ac,
                    "dribbles":       dribbles,
                    "yellow_cards":   yellow,
                    "red_cards":      red,
                })
                player_id += 1

    df = pd.DataFrame(rows)

    # ── Compute rating (attack-focused, scaled 5.0 – 9.5) ────────────────────
    max_goals   = df["goals"].max()
    max_assists = df["assists"].max()
    max_minutes = df["minutes_played"].max()

    score = (
        0.4 * (df["goals"]          / max(max_goals, 1))
      + 0.3 * (df["assists"]        / max(max_assists, 1))
      + 0.2 * (df["pass_accuracy"]  / 100)
      + 0.1 * (df["minutes_played"] / max(max_minutes, 1))
    )
    df["rating"] = (score * (9.5 - 5.0) + 5.0).round(2)

    return df


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = generate_dataset()
    output_path = "football_players.csv"
    df.to_csv(output_path, index=False)

    unique_players = df["player_id"].nunique()
    print(f"✅ Dataset saved to '{output_path}'")
    print(f"   Rows          : {len(df)}")
    print(f"   Unique players: {unique_players}")
    print(f"   Seasons       : {sorted(df['season'].unique())}")
    print(f"   Teams         : {sorted(df['team'].unique())}")
    print(f"   Columns       : {list(df.columns)}")
    print(f"   Note          : {DATA_NOTE}")
