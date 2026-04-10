import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone
import pytz
import io

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dressly · UA Performance Dashboard",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS — Dressly Palette
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #F7F3EE;
    color: #3B2F25;
  }

  /* Main background */
  .main .block-container {
    background-color: #F7F3EE;
    padding: 1.5rem 2rem 3rem 2rem;
    max-width: 1400px;
  }

  /* Metric cards */
  .metric-card {
    background: #F0EAE1;
    border: 1px solid #DDD5CC;
    border-radius: 20px;
    padding: 1.2rem 1.5rem;
    text-align: center;
  }
  .metric-card .label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8B7355;
    margin-bottom: 0.4rem;
  }
  .metric-card .value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #3B2F25;
    line-height: 1;
  }
  .metric-card .delta {
    font-size: 0.78rem;
    font-weight: 500;
    margin-top: 0.3rem;
  }
  .delta-good  { color: #4CAF72; }
  .delta-bad   { color: #E05252; }
  .delta-neutral { color: #8B7355; }

  /* Section headers */
  .section-header {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8B7355;
    margin: 2rem 0 0.8rem 0;
    border-bottom: 1px solid #DDD5CC;
    padding-bottom: 0.4rem;
  }

  /* Signal pills */
  .pill {
    display: inline-block;
    padding: 0.22rem 0.75rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  .pill-scale  { background: #D6F0E0; color: #2A7A4B; }
  .pill-watch  { background: #FFF3CD; color: #7A5A00; }
  .pill-reduce { background: #FFE0E0; color: #8B1A1A; }
  .pill-ok     { background: #EAE4DC; color: #6B5A47; }

  /* Opportunity card */
  .opp-card {
    background: linear-gradient(135deg, #3B2F25 0%, #5C4535 100%);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    color: #F7F3EE;
  }
  .opp-card .opp-title { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; opacity: 0.7; }
  .opp-card .opp-country { font-size: 2rem; font-weight: 700; margin: 0.3rem 0; }
  .opp-card .opp-sub { font-size: 0.85rem; opacity: 0.8; }
  .opp-card .opp-roi { font-size: 1.4rem; font-weight: 700; color: #4CAF72; }

  /* Insight box */
  .insight-box {
    background: #F0EAE1;
    border-left: 4px solid #3B2F25;
    border-radius: 0 16px 16px 0;
    padding: 1rem 1.4rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    line-height: 1.6;
  }

  /* Upload area */
  .upload-hint {
    font-size: 0.78rem;
    color: #8B7355;
    margin-top: 0.3rem;
  }

  /* Hide Streamlit branding */
  #MainMenu, footer { visibility: hidden; }

  /* Streamlit file uploader style override */
  [data-testid="stFileUploader"] {
    background: #F0EAE1;
    border: 2px dashed #DDD5CC;
    border-radius: 16px;
    padding: 0.5rem;
  }

  /* Dataframe */
  [data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
  }

  /* Tabs */
  [data-testid="stTabs"] button {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
  }

  h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #3B2F25 !important; }
  h2 { font-size: 1.1rem !important; font-weight: 600 !important; color: #3B2F25 !important; }
  h3 { font-size: 0.95rem !important; font-weight: 600 !important; color: #3B2F25 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CONSTANTS — GEO TIMEZONE MAP
# ─────────────────────────────────────────────
GEO_TIMEZONE_MAP = {
    "United States": "America/New_York",
    "USA": "America/New_York",
    "US": "America/New_York",
    "United Kingdom": "Europe/London",
    "UK": "Europe/London",
    "Australia": "Australia/Sydney",
    "AU": "Australia/Sydney",
    "Canada": "America/Toronto",
    "CA": "America/Toronto",
    "Ireland": "Europe/Dublin",
    "IE": "Europe/Dublin",
    "South Africa": "Africa/Johannesburg",
    "ZA": "Africa/Johannesburg",
    "Saudi Arabia": "Asia/Riyadh",
    "SA": "Asia/Riyadh",
    "Romania": "Europe/Bucharest",
    "RO": "Europe/Bucharest",
    "Netherlands": "Europe/Amsterdam",
    "NL": "Europe/Amsterdam",
    "United Arab Emirates": "Asia/Dubai",
    "UAE": "Asia/Dubai",
    "Singapore": "Asia/Singapore",
    "SG": "Asia/Singapore",
    "Germany": "Europe/Berlin",
    "DE": "Europe/Berlin",
    "Greece": "Europe/Athens",
    "GR": "Europe/Athens",
    "New Zealand": "Pacific/Auckland",
    "NZ": "Pacific/Auckland",
    "Mexico": "America/Mexico_City",
    "MX": "America/Mexico_City",
    "Belgium": "Europe/Brussels",
    "BE": "Europe/Brussels",
    "Sweden": "Europe/Stockholm",
    "SE": "Europe/Stockholm",
    "Indonesia": "Asia/Jakarta",
    "ID": "Asia/Jakarta",
    "Spain": "Europe/Madrid",
    "ES": "Europe/Madrid",
    "Switzerland": "Europe/Zurich",
    "CH": "Europe/Zurich",
    "Malaysia": "Asia/Kuala_Lumpur",
    "MY": "Asia/Kuala_Lumpur",
    "France": "Europe/Paris",
    "FR": "Europe/Paris",
    "Bulgaria": "Europe/Sofia",
    "BG": "Europe/Sofia",
}

GOLDEN_HOURS_MORNING = (8, 11)   # 08:00–11:00 local
GOLDEN_HOURS_EVENING = (19, 23)  # 19:00–23:00 local
DEAD_HOURS = (1, 5)               # 01:00–05:00 local


# ─────────────────────────────────────────────
#  COLUMN DETECTION HELPERS
# ─────────────────────────────────────────────
def fuzzy_find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first matching column name (case-insensitive, partial match)."""
    cols_lower = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        cand_l = cand.lower()
        # exact
        if cand_l in cols_lower:
            return cols_lower[cand_l]
        # partial
        for col_l, col_orig in cols_lower.items():
            if cand_l in col_l or col_l in cand_l:
                return col_orig
    return None


def normalize_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize hourly dataframe column names."""
    renames = {}

    hour_col = fuzzy_find_col(df, ["event hour", "hour", "time", "hour of day"])
    if hour_col:
        renames[hour_col] = "hour"

    cost_col = fuzzy_find_col(df, ["total cost", "spend", "cost", "amount spent"])
    if cost_col:
        renames[cost_col] = "spend"

    cpm_col = fuzzy_find_col(df, ["cpm", "cost per mille", "cost per 1000"])
    if cpm_col:
        renames[cpm_col] = "cpm"

    cpc_col = fuzzy_find_col(df, ["cpc", "cost per click"])
    if cpc_col:
        renames[cpc_col] = "cpc"

    ctr_col = fuzzy_find_col(df, ["ctr", "click through rate", "click-through"])
    if ctr_col:
        renames[ctr_col] = "ctr"

    cac_col = fuzzy_find_col(df, ["cac", "cost per acquisition", "cost per sub", "cpa"])
    if cac_col:
        renames[cac_col] = "cac"

    cr_col = fuzzy_find_col(df, ["cr to subs", "cr_to_subs", "cr to sub", "conversion rate", "cr"])
    if cr_col:
        renames[cr_col] = "cr"

    subs_col = fuzzy_find_col(df, ["subs1", "subs", "subscriptions", "conversions", "installs"])
    if subs_col:
        renames[subs_col] = "subs"

    df = df.rename(columns=renames)

    # Drop summary/total rows
    if "hour" in df.columns:
        df = df[pd.to_numeric(df["hour"], errors="coerce").notna()].copy()
        df["hour"] = pd.to_numeric(df["hour"]).astype(int)

    # Coerce numeric cols
    for col in ["spend", "cpm", "cpc", "ctr", "cac", "cr", "subs"]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r"[$,%]", "", regex=True).str.strip(),
                errors="coerce"
            )

    return df


def normalize_geo(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize GEO dataframe column names."""
    renames = {}

    country_col = fuzzy_find_col(df, ["country", "breakdown", "geo", "region", "breakdown 1"])
    if country_col:
        renames[country_col] = "country"

    spend_col = fuzzy_find_col(df, ["spend", "total cost", "cost"])
    if spend_col:
        renames[spend_col] = "spend"

    subs_col = fuzzy_find_col(df, ["subs", "subs1", "conversions", "installs", "subscriptions"])
    if subs_col:
        renames[subs_col] = "subs"

    cac_col = fuzzy_find_col(df, ["cac", "cpa", "cost per acquisition"])
    if cac_col:
        renames[cac_col] = "cac"

    roi_col = fuzzy_find_col(df, ["roi 7m", "roi_7m", "roi", "return on investment"])
    if roi_col:
        renames[roi_col] = "roi"

    roas_col = fuzzy_find_col(df, ["roas 0d", "roas_0d", "roas", "return on ad spend"])
    if roas_col:
        renames[roas_col] = "roas"

    cpm_col = fuzzy_find_col(df, ["cpm"])
    if cpm_col:
        renames[cpm_col] = "cpm"

    cr_start_col = fuzzy_find_col(df, ["cr-to-start", "cr_to_start", "cr to start", "cr-start", "open quiz"])
    if cr_start_col:
        renames[cr_start_col] = "cr_to_start"

    clicks_col = fuzzy_find_col(df, ["clicks"])
    if clicks_col:
        renames[clicks_col] = "clicks"

    cpc_col = fuzzy_find_col(df, ["cpc"])
    if cpc_col:
        renames[cpc_col] = "cpc"

    df = df.rename(columns=renames)

    # Drop Grand Total / summary rows
    if "country" in df.columns:
        df = df[~df["country"].astype(str).str.lower().str.contains("grand total|total|all", na=False)].copy()

    # Coerce numerics
    for col in ["spend", "subs", "cac", "roi", "roas", "cpm", "cr_to_start", "clicks", "cpc"]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r"[$,%]", "", regex=True).str.strip(),
                errors="coerce"
            )

    return df


# ─────────────────────────────────────────────
#  TIMEZONE & GOLDEN WINDOW LOGIC
# ─────────────────────────────────────────────
def get_local_hour(country: str, utc_hour: int = None) -> int | None:
    """Return current local hour for a country given UTC hour (defaults to now)."""
    tz_name = GEO_TIMEZONE_MAP.get(country)
    if not tz_name:
        return None
    try:
        tz = pytz.timezone(tz_name)
        if utc_hour is not None:
            now_utc = datetime.now(pytz.utc).replace(hour=utc_hour, minute=0, second=0)
        else:
            now_utc = datetime.now(pytz.utc)
        local_dt = now_utc.astimezone(tz)
        return local_dt.hour
    except Exception:
        return None


def classify_hour(local_hour: int | None) -> str:
    """Return Golden Morning / Golden Evening / Dead Zone / Normal."""
    if local_hour is None:
        return "Unknown"
    if GOLDEN_HOURS_MORNING[0] <= local_hour <= GOLDEN_HOURS_MORNING[1]:
        return "🌅 Golden Morning"
    if GOLDEN_HOURS_EVENING[0] <= local_hour <= GOLDEN_HOURS_EVENING[1]:
        return "🌙 Golden Evening"
    if DEAD_HOURS[0] <= local_hour <= DEAD_HOURS[1]:
        return "💤 Dead Zone"
    return "Normal"


# ─────────────────────────────────────────────
#  SIGNAL ENGINE
# ─────────────────────────────────────────────
def compute_signals(geo_df: pd.DataFrame, hourly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the signal table: one row per GEO with action (SCALE / WATCH / REDUCE / OK).
    """
    avg_cac = hourly_df["cac"].mean() if "cac" in hourly_df.columns else None

    rows = []
    for _, row in geo_df.iterrows():
        country = str(row.get("country", "Unknown"))
        if country in ("nan", "", "Grand Total"):
            continue

        local_h = get_local_hour(country)
        window = classify_hour(local_h)
        local_str = f"{local_h:02d}:xx" if local_h is not None else "N/A"

        spend  = row.get("spend", np.nan)
        subs   = row.get("subs", np.nan)
        cac    = row.get("cac", np.nan)
        roi    = row.get("roi", np.nan)
        cpm    = row.get("cpm", np.nan)
        cr_s   = row.get("cr_to_start", np.nan)

        # Signal logic
        action = "OK"
        reason = "Stable performance."

        if pd.notna(cac) and avg_cac and cac < avg_cac * 0.8:
            if "Golden" in window:
                action = "SCALE"
                reason = f"CAC ${cac:.0f} is {((avg_cac - cac)/avg_cac*100):.0f}% below avg & in {window}."
            elif window != "💤 Dead Zone":
                action = "SCALE"
                reason = f"CAC ${cac:.0f} is {((avg_cac - cac)/avg_cac*100):.0f}% below daily avg."

        if "Dead Zone" in window:
            if pd.notna(cac) and avg_cac and cac > avg_cac * 1.2:
                action = "REDUCE"
                reason = f"In dead hours ({local_str} local). CAC ${cac:.0f} is {((cac - avg_cac)/avg_cac*100):.0f}% above avg."
            elif pd.notna(subs) and subs == 0 and pd.notna(spend) and spend > 50:
                action = "REDUCE"
                reason = f"Zero subs during dead hours. ${spend:.0f} being wasted."

        if pd.notna(cpm) and cpm > 6:
            action = "WATCH"
            reason = f"CPM ${cpm:.2f} — high cost per impression. Monitor creative fatigue."

        if pd.notna(subs) and subs == 0 and pd.notna(spend) and spend > 60:
            action = "REDUCE"
            reason = f"${spend:.0f} spent, 0 subs acquired."

        if pd.notna(roi) and roi > 50 and "Golden" in window:
            action = "SCALE"
            reason = f"ROI {roi:+.0f}% in {window}. Prime scaling window."

        rows.append({
            "Country": country,
            "Local Time": local_str,
            "Window": window,
            "Spend": f"${spend:.0f}" if pd.notna(spend) else "—",
            "Subs": int(subs) if pd.notna(subs) else 0,
            "CAC": f"${cac:.0f}" if pd.notna(cac) else "—",
            "ROI": f"{roi:+.0f}%" if pd.notna(roi) else "—",
            "CPM": f"${cpm:.2f}" if pd.notna(cpm) else "—",
            "CR-to-Start": f"{cr_s:.1f}%" if pd.notna(cr_s) else "—",
            "Action": action,
            "Reason": reason,
            # raw for sorting
            "_cac": cac if pd.notna(cac) else 9999,
            "_roi": roi if pd.notna(roi) else -9999,
            "_spend": spend if pd.notna(spend) else 0,
        })

    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.sort_values("_cac")
    return result


# ─────────────────────────────────────────────
#  CHART HELPERS  (Dressly palette)
# ─────────────────────────────────────────────
PALETTE = {
    "bg":       "#F7F3EE",
    "card":     "#F0EAE1",
    "border":   "#DDD5CC",
    "brown":    "#3B2F25",
    "brown_md": "#5C4535",
    "tan":      "#8B7355",
    "green":    "#4CAF72",
    "red":      "#E05252",
    "amber":    "#F0A500",
}


def chart_hourly_cac_subs(hourly_df: pd.DataFrame) -> go.Figure:
    """Dual-axis line chart: CAC (left) + Subs (right) by hour."""
    df = hourly_df.sort_values("hour")
    avg_cac = df["cac"].mean()

    fig = go.Figure()

    # CAC area + line
    fig.add_trace(go.Scatter(
        x=df["hour"], y=df["cac"],
        name="CAC ($)",
        mode="lines+markers",
        line=dict(color=PALETTE["brown"], width=2.5),
        marker=dict(size=6, color=PALETTE["brown"]),
        fill="tozeroy",
        fillcolor="rgba(59,47,37,0.08)",
        yaxis="y1",
    ))

    # Avg CAC reference line
    fig.add_hline(
        y=avg_cac,
        line_dash="dot",
        line_color=PALETTE["tan"],
        annotation_text=f"Avg ${avg_cac:.0f}",
        annotation_position="top right",
        annotation_font_color=PALETTE["tan"],
        annotation_font_size=11,
    )

    # Subs bars
    if "subs" in df.columns:
        fig.add_trace(go.Bar(
            x=df["hour"], y=df["subs"],
            name="Subs",
            marker_color=PALETTE["green"],
            opacity=0.65,
            yaxis="y2",
        ))

    fig.update_layout(
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["bg"],
        font=dict(family="DM Sans", color=PALETTE["brown"]),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=11),
        ),
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
        xaxis=dict(
            title="Hour (UTC)",
            tickmode="linear", dtick=1,
            gridcolor=PALETTE["border"],
            title_font_size=11,
        ),
        yaxis=dict(
            title="CAC ($)",
            gridcolor=PALETTE["border"],
            title_font_size=11,
        ),
        yaxis2=dict(
            title="Subs",
            overlaying="y",
            side="right",
            showgrid=False,
            title_font_size=11,
        ),
        hovermode="x unified",
    )
    return fig


def chart_hourly_spend(hourly_df: pd.DataFrame) -> go.Figure:
    """Bar chart of spend by hour with CAC color overlay."""
    df = hourly_df.sort_values("hour")
    avg_cac = df["cac"].mean()

    # Color bars by CAC vs avg
    colors = [
        PALETTE["red"] if c > avg_cac * 1.2
        else (PALETTE["green"] if c < avg_cac * 0.8 else PALETTE["tan"])
        for c in df["cac"].fillna(avg_cac)
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["hour"],
        y=df["spend"],
        name="Spend ($)",
        marker_color=colors,
        text=df["cac"].apply(lambda x: f"${x:.0f}" if pd.notna(x) else ""),
        textposition="outside",
        textfont=dict(size=9),
    ))

    fig.update_layout(
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["bg"],
        font=dict(family="DM Sans", color=PALETTE["brown"]),
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,
        xaxis=dict(title="Hour (UTC)", tickmode="linear", dtick=1, gridcolor=PALETTE["border"]),
        yaxis=dict(title="Spend ($)", gridcolor=PALETTE["border"]),
        showlegend=False,
        hovermode="x",
    )
    return fig


def chart_geo_cac_bubble(geo_df: pd.DataFrame) -> go.Figure:
    """Bubble chart: x=CAC, y=ROI, size=Spend, colored by action."""
    action_colors = {
        "SCALE":  PALETTE["green"],
        "WATCH":  PALETTE["amber"],
        "REDUCE": PALETTE["red"],
        "OK":     PALETTE["tan"],
    }
    action_order = ["SCALE", "WATCH", "OK", "REDUCE"]

    fig = go.Figure()
    for action in action_order:
        sub = geo_df[geo_df["Action"] == action]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["_cac"],
            y=sub["_roi"],
            mode="markers+text",
            text=sub["Country"],
            textposition="top center",
            textfont=dict(size=9),
            name=action,
            marker=dict(
                size=sub["_spend"].clip(lower=50).apply(lambda s: max(12, min(50, s / 25))),
                color=action_colors[action],
                line=dict(width=1, color="white"),
                opacity=0.85,
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "CAC: $%{x:.0f}<br>"
                "ROI: %{y:+.0f}%<br>"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["bg"],
        font=dict(family="DM Sans", color=PALETTE["brown"]),
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="CAC ($)", gridcolor=PALETTE["border"], zeroline=False),
        yaxis=dict(title="ROI (%)", gridcolor=PALETTE["border"], zeroline=True,
                   zerolinecolor=PALETTE["border"]),
        hovermode="closest",
    )
    return fig


# ─────────────────────────────────────────────
#  SIGNAL TABLE STYLER
# ─────────────────────────────────────────────
def style_signal_pill(val: str) -> str:
    mapping = {
        "SCALE":  "background:#D6F0E0;color:#2A7A4B;padding:3px 10px;border-radius:999px;font-weight:700;font-size:11px",
        "WATCH":  "background:#FFF3CD;color:#7A5A00;padding:3px 10px;border-radius:999px;font-weight:700;font-size:11px",
        "REDUCE": "background:#FFE0E0;color:#8B1A1A;padding:3px 10px;border-radius:999px;font-weight:700;font-size:11px",
        "OK":     "background:#EAE4DC;color:#6B5A47;padding:3px 10px;border-radius:999px;font-weight:700;font-size:11px",
    }
    return mapping.get(val, "")


# ─────────────────────────────────────────────
#  READ FILE HELPER
# ─────────────────────────────────────────────
def read_uploaded_file(uploaded_file) -> pd.DataFrame | None:
    if uploaded_file is None:
        return None
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif name.endswith((".xlsx", ".xls")):
            return pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file type: {uploaded_file.name}")
            return None
    except Exception as e:
        st.error(f"Error reading {uploaded_file.name}: {e}")
        return None


# ─────────────────────────────────────────────
#  DEMO DATA (for when no files uploaded)
# ─────────────────────────────────────────────
DEMO_HOURLY = pd.DataFrame({
    "hour":  list(range(15)),
    "spend": [399,186,339,359,496,595,684,779,507,542,470,358,321,374,159],
    "cpm":   [4.23,2.93,2.78,2.64,2.29,2.44,3.18,3.62,2.99,3.20,3.33,3.15,3.40,3.97,3.46],
    "cpc":   [0.76,0.63,0.67,0.59,0.51,0.55,0.57,0.59,0.52,0.58,0.52,0.46,0.49,0.57,0.59],
    "ctr":   [0.6,0.5,0.4,0.4,0.4,0.4,0.6,0.6,0.6,0.6,0.6,0.7,0.7,0.7,0.6],
    "cac":   [133.15,62.13,67.85,71.82,165.46,66.08,57.03,155.89,63.39,90.31,93.92,71.60,53.44,46.74,26.51],
    "cr":    [0.50,0.80,0.79,0.63,0.25,0.71,0.83,0.32,0.68,0.53,0.44,0.52,0.65,0.90,1.95],
    "subs":  [3,3,5,5,3,9,12,5,8,6,5,5,6,8,6],
})

DEMO_GEO = pd.DataFrame({
    "country": ["United States","United Kingdom","Australia","Canada","Ireland",
                 "South Africa","Saudi Arabia","Romania","Netherlands","United Arab Emirates",
                 "Singapore","Germany","Greece","New Zealand","Mexico","Belgium",
                 "Sweden","Indonesia","Spain","Switzerland","Malaysia","France","Bulgaria"],
    "spend":   [1398.03,1283.28,558.85,328.16,317.13,239.47,193.34,180.26,150.92,145.97,
                127.95,124.16,115.13,111.54,104.64,92.09,87.65,74.59,70.06,68.79,68.44,61.94,54.59],
    "subs":    [16,20,6,8,0,4,0,4,1,0,5,0,3,2,0,1,1,0,0,2,0,0,1],
    "cac":     [87.38,64.16,93.14,41.02,np.nan,59.87,48.34,45.07,150.92,np.nan,
                25.59,np.nan,38.38,55.77,np.nan,92.09,87.65,np.nan,np.nan,34.40,np.nan,np.nan,54.59],
    "roi":     [-12.58,44.42,-16.39,70.15,0,20.76,66.12,63.60,-57.39,0,
                214.95,0,99.60,15.29,0,-10.14,-26.64,0,0,86.95,0,0,85.37],
    "roas":    [31.66,44.42,30.94,52.59,0,40.44,72.78,63.67,11.61,0,
                123.27,0,85.72,27.24,0,44.07,19.99,0,0,37.87,0,0,116.58],
    "cpm":     [6.01,9.41,8.63,5.37,3.77,2.42,3.74,1.80,4.55,2.98,
                9.17,3.37,1.28,4.57,1.53,2.95,2.88,0.78,1.60,3.03,3.19,2.01,0.72],
    "cr_to_start": [31.72,71.93,45.98,35.69,54.03,61.07,36.36,57.33,65.43,32.57,
                    60.19,55.28,46.22,49.66,15.02,47.59,57.14,5.54,38.33,40.58,40.86,38.10,45.03],
    "clicks":  [967,1087,495,305,365,1013,380,380,217,307,
                233,182,345,167,310,188,168,587,171,85,216,116,219],
})


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
col_logo, col_title, col_ts = st.columns([1, 5, 2])
with col_logo:
    st.markdown("<div style='font-size:2.2rem;margin-top:0.2rem'>👗</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("## Dressly · UA Performance Dashboard")
    st.caption("Facebook + TikTok · Real-time Optimization Engine")
with col_ts:
    now_utc = datetime.now(pytz.utc)
    st.markdown(
        f"<div style='text-align:right;font-size:0.75rem;color:#8B7355;margin-top:0.6rem'>"
        f"🕒 UTC Now: <b>{now_utc.strftime('%H:%M')}</b><br>"
        f"{now_utc.strftime('%d %b %Y')}</div>",
        unsafe_allow_html=True,
    )

st.markdown("<hr style='border:none;border-top:1px solid #DDD5CC;margin:0.3rem 0 1rem 0'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  FILE UPLOADS
# ─────────────────────────────────────────────
col_u1, col_u2 = st.columns(2)
with col_u1:
    st.markdown("**📁 Hourly Report**")
    hourly_file = st.file_uploader("Upload Hourly CSV / Excel", type=["csv","xlsx","xls"], key="hourly", label_visibility="collapsed")
    st.markdown("<p class='upload-hint'>Columns: Event Hour, Total Cost, CPM, CPC, CTR, CAC, CR, Subs</p>", unsafe_allow_html=True)
with col_u2:
    st.markdown("**📁 GEO Report**")
    geo_file = st.file_uploader("Upload GEO CSV / Excel", type=["csv","xlsx","xls"], key="geo", label_visibility="collapsed")
    st.markdown("<p class='upload-hint'>Columns: Country, Spend, Subs, CAC, ROI, ROAS, CPM, CR-to-Start</p>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────
using_demo = False
if hourly_file:
    raw_hourly = read_uploaded_file(hourly_file)
    hourly_df  = normalize_hourly(raw_hourly) if raw_hourly is not None else DEMO_HOURLY.copy()
else:
    hourly_df  = DEMO_HOURLY.copy()
    using_demo = True

if geo_file:
    raw_geo    = read_uploaded_file(geo_file)
    geo_df     = normalize_geo(raw_geo) if raw_geo is not None else DEMO_GEO.copy()
else:
    geo_df     = DEMO_GEO.copy()
    using_demo = True

if using_demo:
    st.info("⚡ Running on **demo data** (04/10/2026 snapshot). Upload your files above to analyze live campaigns.", icon="📊")


# ─────────────────────────────────────────────
#  KPI SUMMARY CARDS
# ─────────────────────────────────────────────
st.markdown("<p class='section-header'>📊 Performance Summary</p>", unsafe_allow_html=True)

total_spend  = hourly_df["spend"].sum()  if "spend"  in hourly_df.columns else 0
total_subs   = hourly_df["subs"].sum()   if "subs"   in hourly_df.columns else 0
avg_cac      = hourly_df["cac"].mean()   if "cac"    in hourly_df.columns else 0
avg_cpm      = hourly_df["cpm"].mean()   if "cpm"    in hourly_df.columns else 0
avg_cr       = hourly_df["cr"].mean()    if "cr"     in hourly_df.columns else 0

# Best hour
if "cac" in hourly_df.columns and not hourly_df.empty:
    best_row   = hourly_df.loc[hourly_df["cac"].idxmin()]
    best_hour  = int(best_row["hour"])
    best_cac   = best_row["cac"]
else:
    best_hour  = 0
    best_cac   = 0

# Last 3 hours trend
last3 = hourly_df.tail(3)
last3_avg_cac = last3["cac"].mean() if "cac" in last3.columns else 0
trend_pct     = ((last3_avg_cac - avg_cac) / avg_cac * 100) if avg_cac else 0
trend_dir     = "📉 Improving" if trend_pct < 0 else "📈 Worsening"
trend_class   = "delta-good"  if trend_pct < 0 else "delta-bad"

c1, c2, c3, c4, c5, c6 = st.columns(6)
cards = [
    (c1, "Total Spend",   f"${total_spend:,.0f}",    None, None),
    (c2, "Total Subs",    f"{int(total_subs)}",       None, None),
    (c3, "Avg CAC",       f"${avg_cac:.2f}",          f"Best: ${best_cac:.0f} @ H{best_hour}", "delta-good"),
    (c4, "Avg CPM",       f"${avg_cpm:.2f}",          None, None),
    (c5, "Avg CR",        f"{avg_cr:.2f}%",           None, None),
    (c6, "Last 3h Trend", f"{trend_pct:+.1f}%",       trend_dir, trend_class),
]
for col, label, val, delta, delta_class in cards:
    with col:
        delta_html = f"<div class='delta {delta_class}'>{delta}</div>" if delta else ""
        st.markdown(f"""
        <div class='metric-card'>
          <div class='label'>{label}</div>
          <div class='value'>{val}</div>
          {delta_html}
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  COMPUTE SIGNALS
# ─────────────────────────────────────────────
signal_df = compute_signals(geo_df, hourly_df)


# ─────────────────────────────────────────────
#  CURRENT OPPORTUNITY CARD
# ─────────────────────────────────────────────
scale_df = signal_df[signal_df["Action"] == "SCALE"].sort_values("_roi", ascending=False)
if not scale_df.empty:
    best_opp = scale_df.iloc[0]
    st.markdown(f"""
    <div class='opp-card'>
      <div class='opp-title'>🚀 Current Best Opportunity</div>
      <div class='opp-country'>{best_opp["Country"]}</div>
      <div class='opp-sub'>{best_opp["Window"]} · Local time {best_opp["Local Time"]} · CAC {best_opp["CAC"]}</div>
      <div class='opp-roi'>{best_opp["ROI"]} ROI</div>
      <div class='opp-sub' style='margin-top:0.5rem;font-size:0.8rem;opacity:0.7'>{best_opp["Reason"]}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CHARTS ROW
# ─────────────────────────────────────────────
st.markdown("<p class='section-header'>📈 Hourly Performance</p>", unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns([3, 2])
with chart_col1:
    st.caption("CAC vs Conversions by Hour")
    st.plotly_chart(chart_hourly_cac_subs(hourly_df), use_container_width=True, config={"displayModeBar": False})
with chart_col2:
    st.caption("Spend by Hour (🟢 Efficient · 🟡 Normal · 🔴 Costly)")
    st.plotly_chart(chart_hourly_spend(hourly_df), use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
#  GEO BUBBLE CHART + SIGNAL TABLE TABS
# ─────────────────────────────────────────────
st.markdown("<p class='section-header'>🌍 GEO Intelligence</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎯 Signal Table", "🫧 CAC vs ROI Map", "📋 Raw Data"])

with tab1:
    # Counts
    n_scale  = (signal_df["Action"] == "SCALE").sum()
    n_watch  = (signal_df["Action"] == "WATCH").sum()
    n_reduce = (signal_df["Action"] == "REDUCE").sum()

    m1, m2, m3 = st.columns(3)
    for col, label, count, pill_cls, emoji in [
        (m1, "Scale Signals",  n_scale,  "pill-scale",  "🚀"),
        (m2, "Watch Signals",  n_watch,  "pill-watch",  "⚠️"),
        (m3, "Reduce Signals", n_reduce, "pill-reduce", "🛑"),
    ]:
        with col:
            st.markdown(
                f"<div style='background:#F0EAE1;border:1px solid #DDD5CC;border-radius:16px;padding:0.8rem 1rem'>"
                f"<span class='pill {pill_cls}'>{emoji} {label}</span>"
                f"<div style='font-size:2rem;font-weight:700;color:#3B2F25;margin-top:0.3rem'>{count}</div>"
                f"</div>", unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    display_cols = ["Country","Local Time","Window","Spend","Subs","CAC","ROI","CPM","CR-to-Start","Action","Reason"]
    display_df   = signal_df[display_cols].copy() if all(c in signal_df.columns for c in display_cols) else signal_df

    def color_action_row(row):
        action_styles = {
            "SCALE":  "background-color:#F0FBF4",
            "WATCH":  "background-color:#FFFBEE",
            "REDUCE": "background-color:#FFF5F5",
            "OK":     "",
        }
        style = action_styles.get(row.get("Action", "OK"), "")
        return [style] * len(row)

    styled = display_df.style.apply(color_action_row, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)

with tab2:
    if not signal_df.empty:
        st.caption("Bubble size = Spend. X = CAC ($). Y = ROI (%). Color = Signal.")
        st.plotly_chart(chart_geo_cac_bubble(signal_df), use_container_width=True, config={"displayModeBar": False})

with tab3:
    raw_tab1, raw_tab2 = st.tabs(["Hourly Raw", "GEO Raw"])
    with raw_tab1:
        st.dataframe(hourly_df, use_container_width=True, hide_index=True)
    with raw_tab2:
        st.dataframe(geo_df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
#  STRATEGIC INSIGHTS
# ─────────────────────────────────────────────
st.markdown("<p class='section-header'>💡 Strategic Insights</p>", unsafe_allow_html=True)

# Auto-generate insights
insights = []

# 1. Best hour insight
if "cac" in hourly_df.columns:
    bh = hourly_df.loc[hourly_df["cac"].idxmin()]
    insights.append(
        f"⭐ <b>Star Hour H{int(bh['hour'])}</b>: CAC <b>${bh['cac']:.0f}</b> — "
        f"<b>{((avg_cac - bh['cac'])/avg_cac*100):.0f}%</b> below daily average. "
        f"Ensure budget is not exhausted before this window."
    )

# 2. Worst hour
if "cac" in hourly_df.columns:
    wh = hourly_df.loc[hourly_df["cac"].idxmax()]
    insights.append(
        f"🔴 <b>Waste Alert H{int(wh['hour'])}</b>: CAC <b>${wh['cac']:.0f}</b> "
        f"({((wh['cac'] - avg_cac)/avg_cac*100):.0f}% above avg) on ${wh['spend']:.0f} spend. "
        f"Implement dayparting or bid caps for this slot."
    )

# 3. Scale target
if not scale_df.empty:
    top = scale_df.iloc[0]
    insights.append(
        f"🚀 <b>Scale Now → {top['Country']}</b>: ROI {top['ROI']} with CAC {top['CAC']}. "
        f"Currently in {top['Window']}. Shift budget from underperforming GEOs immediately."
    )

# 4. Reduce target
reduce_df = signal_df[signal_df["Action"] == "REDUCE"].sort_values("_spend", ascending=False)
if not reduce_df.empty:
    top_r = reduce_df.iloc[0]
    insights.append(
        f"🛑 <b>Cut Spend → {top_r['Country']}</b>: {top_r['Reason']} "
        f"Reallocate freed budget to scaling GEOs."
    )

# 5. CPM watch
high_cpm = signal_df[signal_df["Action"] == "WATCH"].head(2)
if not high_cpm.empty:
    countries = ", ".join(high_cpm["Country"].tolist())
    insights.append(
        f"⚠️ <b>Creative Fatigue Risk</b> in {countries}: CPM above $6. "
        f"Refresh creatives and test new angles for these markets."
    )

for ins in insights:
    st.markdown(f"<div class='insight-box'>{ins}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;font-size:0.72rem;color:#8B7355;padding:1rem 0;border-top:1px solid #DDD5CC'>"
    "Dressly UA Dashboard · Built for Media Buyers · Data refreshes on upload"
    "</div>",
    unsafe_allow_html=True,
)
