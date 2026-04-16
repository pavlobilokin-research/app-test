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
    # ── North America ─────────────────────────
    "United States":                "America/New_York",
    "USA":                          "America/New_York",
    "US":                           "America/New_York",
    "Canada":                       "America/Toronto",
    "CA":                           "America/Toronto",
    "Mexico":                       "America/Mexico_City",
    "MX":                           "America/Mexico_City",
    "Guatemala":                    "America/Guatemala",
    "GT":                           "America/Guatemala",
    "Belize":                       "America/Belize",
    "BZ":                           "America/Belize",
    "Honduras":                     "America/Tegucigalpa",
    "HN":                           "America/Tegucigalpa",
    "El Salvador":                  "America/El_Salvador",
    "SV":                           "America/El_Salvador",
    "Nicaragua":                    "America/Managua",
    "NI":                           "America/Managua",
    "Costa Rica":                   "America/Costa_Rica",
    "CR":                           "America/Costa_Rica",
    "Panama":                       "America/Panama",
    "PA":                           "America/Panama",
    "Cuba":                         "America/Havana",
    "CU":                           "America/Havana",
    "Jamaica":                      "America/Jamaica",
    "JM":                           "America/Jamaica",
    "Haiti":                        "America/Port-au-Prince",
    "HT":                           "America/Port-au-Prince",
    "Dominican Republic":           "America/Santo_Domingo",
    "Dominican Rep":                "America/Santo_Domingo",
    "DO":                           "America/Santo_Domingo",
    "Puerto Rico":                  "America/Puerto_Rico",
    "PR":                           "America/Puerto_Rico",
    "Trinidad and Tobago":          "America/Port_of_Spain",
    "TT":                           "America/Port_of_Spain",
    "Barbados":                     "America/Barbados",
    "BB":                           "America/Barbados",
    "Bahamas":                      "America/Nassau",
    "BS":                           "America/Nassau",

    # ── South America ─────────────────────────
    "Brazil":                       "America/Sao_Paulo",
    "BR":                           "America/Sao_Paulo",
    "Argentina":                    "America/Argentina/Buenos_Aires",
    "AR":                           "America/Argentina/Buenos_Aires",
    "Colombia":                     "America/Bogota",
    "CO":                           "America/Bogota",
    "Chile":                        "America/Santiago",
    "CL":                           "America/Santiago",
    "Peru":                         "America/Lima",
    "PE":                           "America/Lima",
    "Venezuela":                    "America/Caracas",
    "VE":                           "America/Caracas",
    "Ecuador":                      "America/Guayaquil",
    "EC":                           "America/Guayaquil",
    "Bolivia":                      "America/La_Paz",
    "BO":                           "America/La_Paz",
    "Paraguay":                     "America/Asuncion",
    "PY":                           "America/Asuncion",
    "Uruguay":                      "America/Montevideo",
    "UY":                           "America/Montevideo",
    "Guyana":                       "America/Guyana",
    "GY":                           "America/Guyana",
    "Suriname":                     "America/Paramaribo",
    "SR":                           "America/Paramaribo",

    # ── Western Europe ────────────────────────
    "United Kingdom":               "Europe/London",
    "UK":                           "Europe/London",
    "GB":                           "Europe/London",
    "Ireland":                      "Europe/Dublin",
    "IE":                           "Europe/Dublin",
    "France":                       "Europe/Paris",
    "FR":                           "Europe/Paris",
    "Germany":                      "Europe/Berlin",
    "DE":                           "Europe/Berlin",
    "Netherlands":                  "Europe/Amsterdam",
    "NL":                           "Europe/Amsterdam",
    "Belgium":                      "Europe/Brussels",
    "BE":                           "Europe/Brussels",
    "Switzerland":                  "Europe/Zurich",
    "CH":                           "Europe/Zurich",
    "Austria":                      "Europe/Vienna",
    "AT":                           "Europe/Vienna",
    "Spain":                        "Europe/Madrid",
    "ES":                           "Europe/Madrid",
    "Portugal":                     "Europe/Lisbon",
    "PT":                           "Europe/Lisbon",
    "Italy":                        "Europe/Rome",
    "IT":                           "Europe/Rome",
    "Sweden":                       "Europe/Stockholm",
    "SE":                           "Europe/Stockholm",
    "Norway":                       "Europe/Oslo",
    "NO":                           "Europe/Oslo",
    "Denmark":                      "Europe/Copenhagen",
    "DK":                           "Europe/Copenhagen",
    "Finland":                      "Europe/Helsinki",
    "FI":                           "Europe/Helsinki",
    "Luxembourg":                   "Europe/Luxembourg",
    "LU":                           "Europe/Luxembourg",
    "Iceland":                      "Atlantic/Reykjavik",
    "IS":                           "Atlantic/Reykjavik",
    "Liechtenstein":                "Europe/Vaduz",
    "LI":                           "Europe/Vaduz",
    "Monaco":                       "Europe/Monaco",
    "MC":                           "Europe/Monaco",
    "Andorra":                      "Europe/Andorra",
    "AD":                           "Europe/Andorra",

    # ── Central / Eastern Europe ─────────────
    "Poland":                       "Europe/Warsaw",
    "PL":                           "Europe/Warsaw",
    "Czech Republic":               "Europe/Prague",
    "Czechia":                      "Europe/Prague",
    "CZ":                           "Europe/Prague",
    "Slovakia":                     "Europe/Bratislava",
    "SK":                           "Europe/Bratislava",
    "Hungary":                      "Europe/Budapest",
    "HU":                           "Europe/Budapest",
    "Romania":                      "Europe/Bucharest",
    "RO":                           "Europe/Bucharest",
    "Bulgaria":                     "Europe/Sofia",
    "BG":                           "Europe/Sofia",
    "Croatia":                      "Europe/Zagreb",
    "HR":                           "Europe/Zagreb",
    "Serbia":                       "Europe/Belgrade",
    "RS":                           "Europe/Belgrade",
    "Slovenia":                     "Europe/Ljubljana",
    "SI":                           "Europe/Ljubljana",
    "Bosnia and Herzegovina":       "Europe/Sarajevo",
    "Bosnia":                       "Europe/Sarajevo",
    "BA":                           "Europe/Sarajevo",
    "North Macedonia":              "Europe/Skopje",
    "Macedonia":                    "Europe/Skopje",
    "MK":                           "Europe/Skopje",
    "Albania":                      "Europe/Tirane",
    "AL":                           "Europe/Tirane",
    "Kosovo":                       "Europe/Belgrade",
    "XK":                           "Europe/Belgrade",
    "Montenegro":                   "Europe/Podgorica",
    "ME":                           "Europe/Podgorica",
    "Ukraine":                      "Europe/Kiev",
    "UA":                           "Europe/Kiev",
    "Moldova":                      "Europe/Chisinau",
    "MD":                           "Europe/Chisinau",
    "Belarus":                      "Europe/Minsk",
    "BY":                           "Europe/Minsk",
    "Russia":                       "Europe/Moscow",
    "RU":                           "Europe/Moscow",
    "Estonia":                      "Europe/Tallinn",
    "EE":                           "Europe/Tallinn",
    "Latvia":                       "Europe/Riga",
    "LV":                           "Europe/Riga",
    "Lithuania":                    "Europe/Vilnius",
    "LT":                           "Europe/Vilnius",

    # ── Southern Europe / Mediterranean ──────
    "Greece":                       "Europe/Athens",
    "GR":                           "Europe/Athens",
    "Cyprus":                       "Asia/Nicosia",
    "CY":                           "Asia/Nicosia",
    "Malta":                        "Europe/Malta",
    "MT":                           "Europe/Malta",

    # ── Middle East ──────────────────────────
    "United Arab Emirates":         "Asia/Dubai",
    "UAE":                          "Asia/Dubai",
    "AE":                           "Asia/Dubai",
    "Saudi Arabia":                 "Asia/Riyadh",
    "SA":                           "Asia/Riyadh",
    "Kuwait":                       "Asia/Kuwait",
    "KW":                           "Asia/Kuwait",
    "Qatar":                        "Asia/Qatar",
    "QA":                           "Asia/Qatar",
    "Bahrain":                      "Asia/Bahrain",
    "BH":                           "Asia/Bahrain",
    "Oman":                         "Asia/Muscat",
    "OM":                           "Asia/Muscat",
    "Israel":                       "Asia/Jerusalem",
    "IL":                           "Asia/Jerusalem",
    "Jordan":                       "Asia/Amman",
    "JO":                           "Asia/Amman",
    "Lebanon":                      "Asia/Beirut",
    "LB":                           "Asia/Beirut",
    "Syria":                        "Asia/Damascus",
    "SY":                           "Asia/Damascus",
    "Turkey":                       "Europe/Istanbul",
    "TR":                           "Europe/Istanbul",
    "Iran":                         "Asia/Tehran",
    "IR":                           "Asia/Tehran",
    "Iraq":                         "Asia/Baghdad",
    "IQ":                           "Asia/Baghdad",
    "Yemen":                        "Asia/Aden",
    "YE":                           "Asia/Aden",
    "Afghanistan":                  "Asia/Kabul",
    "AF":                           "Asia/Kabul",

    # ── Central Asia ─────────────────────────
    "Kazakhstan":                   "Asia/Almaty",
    "KZ":                           "Asia/Almaty",
    "Uzbekistan":                   "Asia/Tashkent",
    "UZ":                           "Asia/Tashkent",
    "Kyrgyzstan":                   "Asia/Bishkek",
    "KG":                           "Asia/Bishkek",
    "Tajikistan":                   "Asia/Dushanbe",
    "TJ":                           "Asia/Dushanbe",
    "Turkmenistan":                 "Asia/Ashgabat",
    "TM":                           "Asia/Ashgabat",
    "Azerbaijan":                   "Asia/Baku",
    "AZ":                           "Asia/Baku",
    "Armenia":                      "Asia/Yerevan",
    "AM":                           "Asia/Yerevan",
    "Georgia":                      "Asia/Tbilisi",
    "GE":                           "Asia/Tbilisi",

    # ── South Asia ───────────────────────────
    "India":                        "Asia/Kolkata",
    "IN":                           "Asia/Kolkata",
    "Pakistan":                     "Asia/Karachi",
    "PK":                           "Asia/Karachi",
    "Bangladesh":                   "Asia/Dhaka",
    "BD":                           "Asia/Dhaka",
    "Sri Lanka":                    "Asia/Colombo",
    "LK":                           "Asia/Colombo",
    "Nepal":                        "Asia/Kathmandu",
    "NP":                           "Asia/Kathmandu",
    "Maldives":                     "Indian/Maldives",
    "MV":                           "Indian/Maldives",
    "Bhutan":                       "Asia/Thimphu",
    "BT":                           "Asia/Thimphu",

    # ── Southeast Asia ───────────────────────
    "Singapore":                    "Asia/Singapore",
    "SG":                           "Asia/Singapore",
    "Malaysia":                     "Asia/Kuala_Lumpur",
    "MY":                           "Asia/Kuala_Lumpur",
    "Indonesia":                    "Asia/Jakarta",
    "ID":                           "Asia/Jakarta",
    "Thailand":                     "Asia/Bangkok",
    "TH":                           "Asia/Bangkok",
    "Vietnam":                      "Asia/Ho_Chi_Minh",
    "Viet Nam":                     "Asia/Ho_Chi_Minh",
    "VN":                           "Asia/Ho_Chi_Minh",
    "Philippines":                  "Asia/Manila",
    "PH":                           "Asia/Manila",
    "Cambodia":                     "Asia/Phnom_Penh",
    "KH":                           "Asia/Phnom_Penh",
    "Myanmar":                      "Asia/Rangoon",
    "Burma":                        "Asia/Rangoon",
    "MM":                           "Asia/Rangoon",
    "Laos":                         "Asia/Vientiane",
    "LA":                           "Asia/Vientiane",
    "Brunei":                       "Asia/Brunei",
    "BN":                           "Asia/Brunei",
    "Timor-Leste":                  "Asia/Dili",
    "TL":                           "Asia/Dili",

    # ── East Asia ────────────────────────────
    "Japan":                        "Asia/Tokyo",
    "JP":                           "Asia/Tokyo",
    "South Korea":                  "Asia/Seoul",
    "Korea":                        "Asia/Seoul",
    "KR":                           "Asia/Seoul",
    "China":                        "Asia/Shanghai",
    "CN":                           "Asia/Shanghai",
    "Hong Kong":                    "Asia/Hong_Kong",
    "HK":                           "Asia/Hong_Kong",
    "Taiwan":                       "Asia/Taipei",
    "TW":                           "Asia/Taipei",
    "Mongolia":                     "Asia/Ulaanbaatar",
    "MN":                           "Asia/Ulaanbaatar",
    "Macau":                        "Asia/Macau",
    "MO":                           "Asia/Macau",

    # ── Oceania ──────────────────────────────
    "Australia":                    "Australia/Sydney",
    "AU":                           "Australia/Sydney",
    "New Zealand":                  "Pacific/Auckland",
    "NZ":                           "Pacific/Auckland",
    "Papua New Guinea":             "Pacific/Port_Moresby",
    "PG":                           "Pacific/Port_Moresby",
    "Fiji":                         "Pacific/Fiji",
    "FJ":                           "Pacific/Fiji",
    "Solomon Islands":              "Pacific/Guadalcanal",
    "SB":                           "Pacific/Guadalcanal",
    "Vanuatu":                      "Pacific/Efate",
    "VU":                           "Pacific/Efate",
    "Samoa":                        "Pacific/Apia",
    "WS":                           "Pacific/Apia",
    "Tonga":                        "Pacific/Tongatapu",
    "TO":                           "Pacific/Tongatapu",

    # ── North / East Africa ──────────────────
    "Egypt":                        "Africa/Cairo",
    "EG":                           "Africa/Cairo",
    "Ethiopia":                     "Africa/Addis_Ababa",
    "ET":                           "Africa/Addis_Ababa",
    "Kenya":                        "Africa/Nairobi",
    "KE":                           "Africa/Nairobi",
    "Tanzania":                     "Africa/Dar_es_Salaam",
    "TZ":                           "Africa/Dar_es_Salaam",
    "Uganda":                       "Africa/Kampala",
    "UG":                           "Africa/Kampala",
    "Sudan":                        "Africa/Khartoum",
    "SD":                           "Africa/Khartoum",
    "South Sudan":                  "Africa/Juba",
    "SS":                           "Africa/Juba",
    "Somalia":                      "Africa/Mogadishu",
    "SO":                           "Africa/Mogadishu",
    "Rwanda":                       "Africa/Kigali",
    "RW":                           "Africa/Kigali",
    "Burundi":                      "Africa/Bujumbura",
    "BI":                           "Africa/Bujumbura",
    "Djibouti":                     "Africa/Djibouti",
    "DJ":                           "Africa/Djibouti",
    "Eritrea":                      "Africa/Asmara",
    "ER":                           "Africa/Asmara",

    # ── West Africa ──────────────────────────
    "Nigeria":                      "Africa/Lagos",
    "NG":                           "Africa/Lagos",
    "Ghana":                        "Africa/Accra",
    "GH":                           "Africa/Accra",
    "Senegal":                      "Africa/Dakar",
    "SN":                           "Africa/Dakar",
    "Ivory Coast":                  "Africa/Abidjan",
    "Cote d'Ivoire":                "Africa/Abidjan",
    "CI":                           "Africa/Abidjan",
    "Cameroon":                     "Africa/Douala",
    "CM":                           "Africa/Douala",
    "Mali":                         "Africa/Bamako",
    "ML":                           "Africa/Bamako",
    "Burkina Faso":                 "Africa/Ouagadougou",
    "BF":                           "Africa/Ouagadougou",
    "Niger":                        "Africa/Niamey",
    "NE":                           "Africa/Niamey",
    "Guinea":                       "Africa/Conakry",
    "GN":                           "Africa/Conakry",
    "Benin":                        "Africa/Porto-Novo",
    "BJ":                           "Africa/Porto-Novo",
    "Togo":                         "Africa/Lome",
    "TG":                           "Africa/Lome",
    "Sierra Leone":                 "Africa/Freetown",
    "SL":                           "Africa/Freetown",
    "Liberia":                      "Africa/Monrovia",
    "LR":                           "Africa/Monrovia",
    "Gambia":                       "Africa/Banjul",
    "GM":                           "Africa/Banjul",
    "Guinea-Bissau":                "Africa/Bissau",
    "GW":                           "Africa/Bissau",
    "Mauritania":                   "Africa/Nouakchott",
    "MR":                           "Africa/Nouakchott",
    "Cape Verde":                   "Atlantic/Cape_Verde",
    "CV":                           "Atlantic/Cape_Verde",

    # ── Central Africa ───────────────────────
    "DR Congo":                     "Africa/Kinshasa",
    "Democratic Republic of Congo": "Africa/Kinshasa",
    "Congo":                        "Africa/Brazzaville",
    "CD":                           "Africa/Kinshasa",
    "CG":                           "Africa/Brazzaville",
    "Central African Republic":     "Africa/Bangui",
    "CF":                           "Africa/Bangui",
    "Chad":                         "Africa/Ndjamena",
    "TD":                           "Africa/Ndjamena",
    "Gabon":                        "Africa/Libreville",
    "GA":                           "Africa/Libreville",
    "Equatorial Guinea":            "Africa/Malabo",
    "GQ":                           "Africa/Malabo",
    "Sao Tome and Principe":        "Africa/Sao_Tome",
    "ST":                           "Africa/Sao_Tome",

    # ── Southern Africa ──────────────────────
    "South Africa":                 "Africa/Johannesburg",
    "ZA":                           "Africa/Johannesburg",
    "Zimbabwe":                     "Africa/Harare",
    "ZW":                           "Africa/Harare",
    "Zambia":                       "Africa/Lusaka",
    "ZM":                           "Africa/Lusaka",
    "Mozambique":                   "Africa/Maputo",
    "MZ":                           "Africa/Maputo",
    "Madagascar":                   "Indian/Antananarivo",
    "MG":                           "Indian/Antananarivo",
    "Malawi":                       "Africa/Blantyre",
    "MW":                           "Africa/Blantyre",
    "Botswana":                     "Africa/Gaborone",
    "BW":                           "Africa/Gaborone",
    "Namibia":                      "Africa/Windhoek",
    "NA":                           "Africa/Windhoek",
    "Lesotho":                      "Africa/Maseru",
    "LS":                           "Africa/Maseru",
    "Eswatini":                     "Africa/Mbabane",
    "Swaziland":                    "Africa/Mbabane",
    "SZ":                           "Africa/Mbabane",
    "Angola":                       "Africa/Luanda",
    "AO":                           "Africa/Luanda",

    # ── North Africa ─────────────────────────
    "Morocco":                      "Africa/Casablanca",
    "MA":                           "Africa/Casablanca",
    "Algeria":                      "Africa/Algiers",
    "DZ":                           "Africa/Algiers",
    "Tunisia":                      "Africa/Tunis",
    "TN":                           "Africa/Tunis",
    "Libya":                        "Africa/Tripoli",
    "LY":                           "Africa/Tripoli",
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


def _parse_numeric(val) -> float | None:
    """Strip currency/space/comma, parse as float. For currency columns."""
    try:
        cleaned = str(val).replace("US$", "").replace("$", "").replace("%", "")
        cleaned = cleaned.replace(",", ".").replace("\xa0", "").replace(" ", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def _parse_pct(val) -> float | None:
    """Parse a percentage that may be stored as:
    - Excel internal decimal: 0.0057 -> 0.57  (Excel stores 0.57% as 0.0057)
    - String with % sign   : "0,57%" -> 0.57
    - String without %     : "0.57"  -> 0.57  (assume already in % units)
    Rule: if raw value has no % AND parsed float < 1.0, multiply x100.
    """
    raw_str = str(val)
    has_pct = "%" in raw_str
    try:
        cleaned = raw_str.replace("US$","").replace("$","").replace("%","")
        cleaned = cleaned.replace(",",".").replace("\xa0","").replace(" ","").strip()
        num = float(cleaned)
        if not has_pct and num < 1.0:
            return round(num * 100, 4)
        return num
    except (ValueError, TypeError):
        return None



def normalize_hourly(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Standardize hourly dataframe column names.
    
    Returns (hourly_df, grand_total) where grand_total is a dict
    with values read directly from the Grand Total row — no calculations.
    """
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

    df_renamed = df.rename(columns=renames)

    # ── Extract Grand Total row BEFORE dropping it ─────────────────────────
    # Grand Total row = the row where the hour column is non-numeric
    # (contains text like "Grand Total") AND the row contains "total" somewhere.
    grand_total: dict = {}
    if "hour" in df_renamed.columns:
        hour_is_text = pd.to_numeric(
            df_renamed["hour"].astype(str)
                .str.replace(r"[US$\s,.]", "", regex=True),
            errors="coerce",
        ).isna()
        has_total_text = df_renamed.apply(
            lambda row: row.astype(str).str.lower().str.contains("total").any(), axis=1
        )
        gt_rows = df_renamed[hour_is_text & has_total_text]
        if not gt_rows.empty:
            gt_row = gt_rows.iloc[0]
            _pct_cols = {"cr", "ctr"}
            for col in ["spend", "cpm", "cpc", "ctr", "cac", "cr", "subs"]:
                if col in gt_row.index:
                    parser = _parse_pct if col in _pct_cols else _parse_numeric
                    val = parser(gt_row[col])
                    if val is not None:
                        grand_total[col] = val

    # ── Drop summary/total rows (keep only numeric hour rows) ──────────────
    if "hour" in df_renamed.columns:
        df_renamed = df_renamed[pd.to_numeric(df_renamed["hour"], errors="coerce").notna()].copy()
        df_renamed["hour"] = pd.to_numeric(df_renamed["hour"]).astype(int)

    # ── Coerce numeric cols ────────────────────────────────────────────────
    _pct_cols = {"cr", "ctr"}
    for col in ["spend", "cpm", "cpc", "ctr", "cac", "cr", "subs"]:
        if col in df_renamed.columns:
            parser = _parse_pct if col in _pct_cols else _parse_numeric
            df_renamed[col] = df_renamed[col].apply(parser)

    return df_renamed, grand_total


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
def _resolve_tz(country: str) -> str | None:
    """
    Resolve a timezone string for any country name or ISO-2 code.
    Priority: 1) GEO_TIMEZONE_MAP exact match
              2) GEO_TIMEZONE_MAP case-insensitive match
              3) pytz.country_timezones lookup by ISO-2 code
              4) fuzzy scan of pytz.country_names
    """
    # 1. Exact match
    if country in GEO_TIMEZONE_MAP:
        return GEO_TIMEZONE_MAP[country]
    # 2. Case-insensitive match
    country_lower = country.lower().strip()
    for k, v in GEO_TIMEZONE_MAP.items():
        if k.lower() == country_lower:
            return v
    # 3. pytz country_timezones — try as ISO-2 code
    upper = country.upper().strip()
    if upper in pytz.country_timezones:
        tzs = pytz.country_timezones[upper]
        return tzs[0] if tzs else None
    # 4. Scan pytz.country_names for full name match
    for iso2, name in pytz.country_names.items():
        if name.lower() == country_lower:
            tzs = pytz.country_timezones.get(iso2, [])
            return tzs[0] if tzs else None
    return None


def get_local_hour(country: str, utc_hour: int = None) -> int | None:
    """Return current local hour for a country given UTC hour (defaults to now)."""
    tz_name = _resolve_tz(country)
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
    """Bubble chart: x=CAC, y=ROI (%), size=Spend, colored by action.
    
    ROI values are stored as plain percentages (e.g. 44.42 = 44.42%).
    We filter out sentinel/placeholder _cac values (9999) and _roi (-9999)
    so the axis stays meaningful.
    """
    action_colors = {
        "SCALE":  PALETTE["green"],
        "WATCH":  PALETTE["amber"],
        "REDUCE": PALETTE["red"],
        "OK":     PALETTE["tan"],
    }
    action_order = ["SCALE", "WATCH", "OK", "REDUCE"]

    # Strip rows with sentinel values (no real CAC or ROI data)
    plot_df = geo_df[(geo_df["_cac"] < 9000) & (geo_df["_roi"] > -9000)].copy()

    if plot_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data with valid CAC & ROI to display.",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, font=dict(color=PALETTE["tan"]))
        fig.update_layout(paper_bgcolor=PALETTE["bg"], plot_bgcolor=PALETTE["bg"],
                          height=300, margin=dict(l=10,r=10,t=10,b=10))
        return fig

    # Compute clean axis ranges with padding
    cac_max = plot_df["_cac"].max()
    roi_min = plot_df["_roi"].min()
    roi_max = plot_df["_roi"].max()
    cac_pad = max(cac_max * 0.15, 20)
    roi_pad = max(abs(roi_max - roi_min) * 0.15, 10)

    fig = go.Figure()
    for action in action_order:
        sub = plot_df[plot_df["Action"] == action]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["_cac"],
            y=sub["_roi"],          # already in % (e.g. 44.42 = 44.42%)
            mode="markers+text",
            text=sub["Country"],
            textposition="top center",
            textfont=dict(size=9, color=PALETTE["brown"]),
            name=action,
            marker=dict(
                size=sub["_spend"].clip(lower=30).apply(lambda s: max(14, min(55, s / 20))),
                color=action_colors[action],
                line=dict(width=1.5, color="white"),
                opacity=0.88,
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "CAC: $%{x:.0f}<br>"
                "ROI: %{y:+.1f}%<br>"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["bg"],
        font=dict(family="DM Sans", color=PALETTE["brown"]),
        height=420,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11)),
        xaxis=dict(
            title="CAC ($)",
            gridcolor=PALETTE["border"],
            zeroline=False,
            range=[-cac_pad, cac_max + cac_pad],
            tickprefix="$",
        ),
        yaxis=dict(
            title="ROI (%)",
            gridcolor=PALETTE["border"],
            zeroline=True,
            zerolinecolor="#C8BEB4",
            zerolinewidth=1.5,
            range=[roi_min - roi_pad, roi_max + roi_pad],
            ticksuffix="%",
        ),
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
# Non-blocking data load — Tab 1 always works, tabs 2-5 check for data
_files_ready = False
hourly_df = None
hourly_grand_total = {}
geo_df = None

if hourly_file:
    _raw_hourly = read_uploaded_file(hourly_file)
    if _raw_hourly is not None:
        hourly_df, hourly_grand_total = normalize_hourly(_raw_hourly)

if geo_file:
    _raw_geo = read_uploaded_file(geo_file)
    if _raw_geo is not None:
        geo_df = normalize_geo(_raw_geo)

_files_ready = (hourly_df is not None and geo_df is not None)



# ─────────────────────────────────────────────
#  UPLOAD GATE HELPER (used inside each performance tab)
# ─────────────────────────────────────────────
def _upload_gate_inline():
    missing = []
    if not hourly_file: missing.append("📁 Hourly Report")
    if not geo_file:    missing.append("📁 GEO Report")
    missing_str = " &amp; ".join(missing)
    st.markdown(f"""
    <div style="background:#F0EAE1;border:2px dashed #DDD5CC;border-radius:20px;
         padding:2.5rem 2rem;text-align:center;margin-top:1rem">
      <div style="font-size:2rem;margin-bottom:0.6rem">📊</div>
      <div style="font-size:1rem;font-weight:700;color:#3B2F25;margin-bottom:0.4rem">
        Upload both files to view this tab
      </div>
      <div style="font-size:0.85rem;color:#8B7355">
        {missing_str} needed — use the uploaders at the top of the page
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MAIN TABS
# ─────────────────────────────────────────────
main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6 = st.tabs([
    "🌍 World Clock & Holidays",
    "📊 Performance Summary",
    "📈 Hourly Analysis",
    "🎯 GEO Signals",
    "💡 Strategic Verdict",
    "📅 Marketing Calendar",
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — WORLD CLOCK & HOLIDAYS
# ══════════════════════════════════════════════════════════════════════════════
with main_tab1:

    now_utc_wc = datetime.now(pytz.utc)

    # ── Holiday engine ────────────────────────────────────────────────────────
    import holidays as hol_lib

    COUNTRY_ISO = {
        "United States":        "US",
        "United Arab Emirates": "AE",
        "Austria":              "AT",
        "Australia":            "AU",
        "Belgium":              "BE",
        "Bulgaria":             "BG",
        "Canada":               "CA",
        "Switzerland":          "CH",
        "Chile":                "CL",
        "Colombia":             "CO",
        "Costa Rica":           "CR",
        "Czech Republic":       "CZ",
        "Germany":              "DE",
        "Denmark":              "DK",
        "Dominican Republic":   "DO",
        "Ecuador":              "EC",
        "Estonia":              "EE",
        "Spain":                "ES",
        "Finland":              "FI",
        "France":               "FR",
        "United Kingdom":       "GB",
        "Greece":               "GR",
        "Croatia":              "HR",
        "Hungary":              "HU",
        "Indonesia":            "ID",
        "Ireland":              "IE",
        "Israel":               "IL",
        "Italy":                "IT",
        "Jordan":               "JO",
        "South Korea":          "KR",
        "Kuwait":               "KW",
        "Lithuania":            "LT",
        "Latvia":               "LV",
        "Morocco":              "MA",
        "Mexico":               "MX",
        "Malaysia":             "MY",
        "Netherlands":          "NL",
        "New Zealand":          "NZ",
        "Oman":                 "OM",
        "Panama":               "PA",
        "Poland":               "PL",
        "Portugal":             "PT",
        "Qatar":                "QA",
        "Romania":              "RO",
        "Serbia":               "RS",
        "Saudi Arabia":         "SA",
        "Singapore":            "SG",
        "Slovenia":             "SI",
        "Slovakia":             "SK",
        "Sweden":               "SE",
        "Thailand":             "TH",
        "Turkey":               "TR",
        "Taiwan":               "TW",
        "South Africa":         "ZA",
    }

    COUNTRY_FLAG = {
        "United States":"🇺🇸","United Arab Emirates":"🇦🇪","Austria":"🇦🇹",
        "Australia":"🇦🇺","Belgium":"🇧🇪","Bulgaria":"🇧🇬","Canada":"🇨🇦",
        "Switzerland":"🇨🇭","Chile":"🇨🇱","Colombia":"🇨🇴","Costa Rica":"🇨🇷",
        "Czech Republic":"🇨🇿","Germany":"🇩🇪","Denmark":"🇩🇰",
        "Dominican Republic":"🇩🇴","Ecuador":"🇪🇨","Estonia":"🇪🇪",
        "Spain":"🇪🇸","Finland":"🇫🇮","France":"🇫🇷","United Kingdom":"🇬🇧",
        "Greece":"🇬🇷","Croatia":"🇭🇷","Hungary":"🇭🇺","Indonesia":"🇮🇩",
        "Ireland":"🇮🇪","Israel":"🇮🇱","Italy":"🇮🇹","Jordan":"🇯🇴",
        "South Korea":"🇰🇷","Kuwait":"🇰🇼","Lithuania":"🇱🇹","Latvia":"🇱🇻",
        "Morocco":"🇲🇦","Mexico":"🇲🇽","Malaysia":"🇲🇾","Netherlands":"🇳🇱",
        "New Zealand":"🇳🇿","Oman":"🇴🇲","Panama":"🇵🇦","Poland":"🇵🇱",
        "Portugal":"🇵🇹","Qatar":"🇶🇦","Romania":"🇷🇴","Serbia":"🇷🇸",
        "Saudi Arabia":"🇸🇦","Singapore":"🇸🇬","Slovenia":"🇸🇮","Slovakia":"🇸🇰",
        "Sweden":"🇸🇪","Thailand":"🇹🇭","Turkey":"🇹🇷","Taiwan":"🇹🇼",
        "South Africa":"🇿🇦",
    }

    # States in the exact requested order, with representative city timezone
    US_STATES = [
        ("Texas",           "America/Chicago",       "TX"),
        ("California",      "America/Los_Angeles",   "CA"),
        ("Florida",         "America/New_York",      "FL"),
        ("New York",        "America/New_York",      "NY"),
        ("Georgia",         "America/New_York",      "GA"),
        ("Illinois",        "America/Chicago",       "IL"),
        ("North Carolina",  "America/New_York",      "NC"),
        ("Pennsylvania",    "America/New_York",      "PA"),
        ("Ohio",            "America/New_York",      "OH"),
        ("New Jersey",      "America/New_York",      "NJ"),
        ("Virginia",        "America/New_York",      "VA"),
        ("Michigan",        "America/Detroit",       "MI"),
        ("Colorado",        "America/Denver",        "CO"),
        ("Washington",      "America/Los_Angeles",   "WA"),
        ("Tennessee",       "America/Chicago",       "TN"),
        ("Massachusetts",   "America/New_York",      "MA"),
        ("Indiana",         "America/Indiana/Indianapolis", "IN"),
    ]

    US_STATE_ISO = {s[0]: s[2] for s in US_STATES}

    def get_holidays_for_year(iso2: str, year: int) -> dict:
        """Return {date: name} dict for a country/year, always in English."""
        try:
            h = hol_lib.country_holidays(iso2, years=year)
            # Use English if the country supports it
            try:
                if "en_US" in h.supported_languages:
                    h = hol_lib.country_holidays(iso2, years=year, language="en_US")
            except Exception:
                pass
            return dict(h)
        except Exception:
            return {}

    def get_us_state_holidays(state_iso: str, year: int) -> dict:
        try:
            return dict(hol_lib.US(state=state_iso, years=year))
        except Exception:
            return {}

    today = now_utc_wc.date()
    cur_year  = today.year
    next_year = cur_year + 1

    def upcoming_holidays(iso2: str, n: int = 3, state_iso: str = None) -> list[tuple]:
        """Return up to n upcoming holidays as (date, name) sorted by date."""
        combined = {}
        for yr in [cur_year, next_year]:
            if state_iso:
                combined.update(get_us_state_holidays(state_iso, yr))
            else:
                combined.update(get_holidays_for_year(iso2, yr))
        future = sorted(
            [(d, name) for d, name in combined.items() if d >= today],
            key=lambda x: x[0]
        )
        return future[:n]

    def today_holiday(iso2: str, state_iso: str = None) -> str | None:
        h = get_holidays_for_year(iso2, cur_year)
        if state_iso:
            h.update(get_us_state_holidays(state_iso, cur_year))
        return h.get(today)

    def window_label(local_hour: int) -> tuple[str, str]:
        """Return (window_name, bg_color) for a local hour."""
        if 8 <= local_hour <= 11:
            return "🌅 Morning Peak", "#FFF8E6"
        if 19 <= local_hour <= 23:
            return "🌙 Evening Peak", "#EEF0FF"
        if 1 <= local_hour <= 5:
            return "💤 Dead Zone", "#F0EAE1"
        return "🕐 Normal", "#FFFFFF"

    # ── Search + filter ───────────────────────────────────────────────────────
    wc_col1, wc_col2, wc_col3 = st.columns([3, 2, 2])
    with wc_col1:
        search_q = st.text_input("🔍 Search country", placeholder="e.g. Germany, Singapore…", label_visibility="collapsed")
    with wc_col2:
        window_filter = st.selectbox("Filter by window", ["All Windows", "Morning Peak", "Evening Peak", "Dead Zone", "Normal"], label_visibility="collapsed")
    with wc_col3:
        holiday_only = st.checkbox("🎉 Show holidays only (today)", value=False)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Build rows ────────────────────────────────────────────────────────────
    def build_clock_rows():
        rows = []

        # ── USA first — collapsible country row + states ─────────────────────
        us_iso  = "US"
        us_flag = "🇺🇸"
        us_fed_hol = today_holiday(us_iso)

        et_tz    = pytz.timezone("America/New_York")
        et_local = now_utc_wc.astimezone(et_tz)
        et_h     = et_local.hour
        win_label, win_bg = window_label(et_h)
        us_expanded = st.session_state.get("us_expanded", False)
        toggle_label = "▼ United States (click to collapse)" if us_expanded else "▶ United States (click to expand states)"
        rows.append({
            "flag": us_flag,
            "country": "United States",
            "detail": "Federal",
            "tz_str": "Multiple",
            "local_time": "—",
            "local_hour": et_h,
            "window": win_label,
            "win_bg": win_bg,
            "today_hol": us_fed_hol or "",
            "upcoming": upcoming_holidays(us_iso, n=3),
            "is_state": False,
            "is_country_header": True,
            "toggle_label": toggle_label,
            "us_expanded": us_expanded,
        })

        if us_expanded:
            for state_name, tz_str, tz_code in US_STATES:
                state_iso = US_STATE_ISO[state_name]
                tz_obj    = pytz.timezone(tz_str)
                local_dt  = now_utc_wc.astimezone(tz_obj)
                lh        = local_dt.hour
                wl, wb    = window_label(lh)
                state_hol = today_holiday(us_iso, state_iso=state_iso)
                rows.append({
                    "flag": "  ",
                    "country": f"  {state_name}",
                    "detail": tz_code,
                    "tz_str": tz_str,
                    "local_time": local_dt.strftime("%H:%M"),
                    "local_hour": lh,
                    "window": wl,
                    "win_bg": wb,
                    "today_hol": state_hol or "",
                    "upcoming": upcoming_holidays(us_iso, n=2, state_iso=state_iso),
                    "is_state": True,
                    "is_country_header": False,
                })

        # ── All other countries alphabetically ───────────────────────────────
        for country in sorted(COUNTRY_ISO.keys()):
            iso2   = COUNTRY_ISO[country]
            flag   = COUNTRY_FLAG.get(country, "")
            tz_name = _resolve_tz(country)
            if not tz_name:
                continue
            tz_obj   = pytz.timezone(tz_name)
            local_dt = now_utc_wc.astimezone(tz_obj)
            lh       = local_dt.hour
            wl, wb   = window_label(lh)
            t_hol    = today_holiday(iso2)
            rows.append({
                "flag": flag,
                "country": country,
                "detail": tz_obj.zone,
                "tz_str": tz_name,
                "local_time": local_dt.strftime("%H:%M"),
                "local_hour": lh,
                "window": wl,
                "win_bg": wb,
                "today_hol": t_hol or "",
                "upcoming": upcoming_holidays(iso2, n=3),
                "is_state": False,
                "is_country_header": False,
            })
        return rows

    all_rows = build_clock_rows()

    # Apply filters
    filtered = all_rows
    if search_q:
        q = search_q.lower()
        filtered = [r for r in filtered if q in r["country"].lower()]
    if window_filter != "All Windows":
        filtered = [r for r in filtered if window_filter in r["window"]]
    if holiday_only:
        filtered = [r for r in filtered if r["today_hol"]]

    # ── Render cards ─────────────────────────────────────────────────────────
    COLS = 3
    col_groups = [filtered[i:i+COLS] for i in range(0, len(filtered), COLS)]

    def render_upcoming(upcoming_list):
        if not upcoming_list:
            return "<span style='color:#8B7355;font-size:0.72rem'>No upcoming holidays found</span>"
        parts = []
        for d, name in upcoming_list:
            days_away = (d - today).days
            if days_away == 0:
                label = "<b style='color:#E05252'>TODAY</b>"
            elif days_away == 1:
                label = "<b style='color:#F0A500'>Tomorrow</b>"
            elif days_away <= 7:
                label = f"<b style='color:#4CAF72'>in {days_away}d</b>"
            else:
                label = f"in {days_away}d"
            parts.append(
                f"<div style='padding:0.12rem 0;border-bottom:1px solid #EDE6DC;font-size:0.74rem'>"
                f"<span style='color:#8B7355'>{d.strftime('%b %d')}</span> "
                f"<span style='color:#3B2F25'>{name}</span> "
                f"<span style='color:#8B7355'>{label}</span></div>"
            )
        return "".join(parts)

    if not filtered:
        st.markdown(
            "<div style='text-align:center;color:#8B7355;padding:3rem'>No countries match your filter.</div>",
            unsafe_allow_html=True
        )
    else:
        for row_group in col_groups:
            cols = st.columns(COLS)
            for col_obj, row in zip(cols, row_group):
                with col_obj:
                    if row["is_country_header"]:
                        hol_html = (f'<div style="margin-top:0.5rem;background:#4CAF72;border-radius:8px;'
                                    f'padding:0.2rem 0.5rem;font-size:0.7rem;color:white;font-weight:700">'
                                    f'🎉 {row["today_hol"]}</div>') if row["today_hol"] else ""
                        st.markdown(f"""
                        <div style="background:#3B2F25;border-radius:16px;padding:1rem 1.2rem;margin-bottom:0.6rem">
                          <div style="display:flex;justify-content:space-between;align-items:center">
                            <span style="font-size:1.2rem">{row['flag']}</span>
                            <span style="font-size:0.65rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#DDD5CC">{row['country']}</span>
                            <span style="font-size:0.7rem;color:#8B7355">{row['detail']}</span>
                          </div>
                          {hol_html}
                        </div>
                        """, unsafe_allow_html=True)
                        # Toggle button rendered as a real Streamlit button
                        toggle_lbl = row.get("toggle_label", "▶ Expand states")
                        if st.button(toggle_lbl, key="us_toggle", use_container_width=True):
                            st.session_state["us_expanded"] = not st.session_state.get("us_expanded", False)
                            st.rerun()
                    else:
                        hol_badge = ""
                        if row["today_hol"]:
                            hol_badge = f"<div style='margin-top:0.4rem;background:#4CAF72;border-radius:8px;padding:0.15rem 0.5rem;font-size:0.68rem;color:white;font-weight:700;display:inline-block'>🎉 {row['today_hol']}</div>"

                        indent = "padding-left:1.2rem;border-left:3px solid #DDD5CC;" if row["is_state"] else ""
                        upcoming_html = render_upcoming(row["upcoming"])

                        st.markdown(f"""
                        <div style="background:{row['win_bg']};border:1px solid #DDD5CC;border-radius:16px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;{indent}">
                          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem">
                            <div>
                              <span style="font-size:1rem">{row['flag']}</span>
                              <span style="font-weight:700;font-size:0.88rem;color:#3B2F25;margin-left:0.3rem">{row['country'].strip()}</span>
                              <span style="font-size:0.68rem;color:#8B7355;margin-left:0.3rem">{row['detail'].split('/')[-1] if '/' in row['detail'] else row['detail']}</span>
                            </div>
                            <div style="text-align:right">
                              <div style="font-size:1.35rem;font-weight:700;color:#3B2F25;line-height:1">{row['local_time']}</div>
                              <div style="font-size:0.65rem;color:#8B7355">{row['window']}</div>
                            </div>
                          </div>
                          {hol_badge}
                          <div style="margin-top:0.5rem">{upcoming_html}</div>
                        </div>
                        """, unsafe_allow_html=True)

    # ── Holiday legend ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#F0EAE1;border-radius:12px;padding:0.7rem 1rem;font-size:0.72rem;color:#8B7355;display:flex;gap:1.5rem;flex-wrap:wrap">
      <b>Window legend:</b>
      <span style="background:#FFF8E6;padding:0.15rem 0.5rem;border-radius:6px">🌅 Morning Peak 08–11</span>
      <span style="background:#EEF0FF;padding:0.15rem 0.5rem;border-radius:6px">🌙 Evening Peak 19–23</span>
      <span style="background:#F0EAE1;padding:0.15rem 0.5rem;border-radius:6px">💤 Dead Zone 01–05</span>
      <span style="padding:0.15rem 0.5rem;border-radius:6px">🕐 Normal hours</span>
      <span style="background:#4CAF72;color:white;padding:0.15rem 0.5rem;border-radius:6px">🎉 Public holiday today</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TABS 2–5 — PERFORMANCE DASHBOARD (requires files)
# ══════════════════════════════════════════════════════════════════════════════

# ── File uploads (shown in all performance tabs via sidebar-style placement) ──
with main_tab2:
    _show_upload = not (hourly_file and geo_file)

with main_tab3:
    _show_upload3 = not (hourly_file and geo_file)

# Gate: show upload prompt inside each performance tab if files missing
def _upload_gate():
    missing = []
    if not hourly_file: missing.append("📁 Hourly Report")
    if not geo_file:    missing.append("📁 GEO Report")
    if missing:
        st.markdown(f"""
        <div style="background:#F0EAE1;border:2px dashed #DDD5CC;border-radius:20px;
             padding:2.5rem 2rem;text-align:center;margin-top:1rem">
          <div style="font-size:2rem;margin-bottom:0.6rem">📊</div>
          <div style="font-size:1rem;font-weight:700;color:#3B2F25;margin-bottom:0.4rem">
            Upload both files to view this tab
          </div>
          <div style="font-size:0.85rem;color:#8B7355">
            {" &amp; ".join(missing)} needed — use the uploaders at the top of the page
          </div>
        </div>
        """, unsafe_allow_html=True)
        return False
    return True



# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — PERFORMANCE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
with main_tab2:
    if not _files_ready:
        _upload_gate_inline()
    else:
        # ── All KPI values come directly from the Grand Total row ─────────────
        def _gt(key, fallback):
            return hourly_grand_total.get(key, fallback)

        total_spend = _gt("spend", hourly_df["spend"].sum() if "spend" in hourly_df.columns else 0)
        total_subs  = _gt("subs",  hourly_df["subs"].sum()  if "subs"  in hourly_df.columns else 0)
        avg_cac     = _gt("cac",   0)
        avg_cpm     = _gt("cpm",   0)
        avg_cr      = _gt("cr",    0)
        avg_cpc     = _gt("cpc",   0)
        avg_ctr     = _gt("ctr",   0)
        _from_gt    = bool(hourly_grand_total)

        # Best hour
        if "cac" in hourly_df.columns and not hourly_df.empty:
            best_row  = hourly_df.loc[hourly_df["cac"].idxmin()]
            best_hour = int(best_row["hour"])
            best_cac  = best_row["cac"]
        else:
            best_hour = 0; best_cac = 0

        # Last 3h trend
        last3 = hourly_df.tail(3)
        last3_avg_cac = last3["cac"].mean() if "cac" in last3.columns else 0
        trend_pct     = ((last3_avg_cac - avg_cac) / avg_cac * 100) if avg_cac else 0
        trend_dir     = "📉 Improving" if trend_pct < 0 else "📈 Worsening"
        trend_class   = "delta-good"  if trend_pct < 0 else "delta-bad"

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        cards = [
            (c1, "Total Spend",        f"${total_spend:,.0f}",  None, None),
            (c2, "Total Subs",         f"{int(total_subs)}",    None, None),
            (c3, "CAC (Grand Total)",  f"${avg_cac:.2f}",       f"Best: ${best_cac:.0f} @ H{best_hour}", "delta-good"),
            (c4, "CPM (Grand Total)",  f"${avg_cpm:.2f}",       "From Grand Total row" if _from_gt else "Calculated", "delta-neutral"),
            (c5, "CR (Grand Total)",   f"{avg_cr:.2f}%",        "From Grand Total row" if _from_gt else "Calculated", "delta-neutral"),
            (c6, "Last 3h Trend",      f"{trend_pct:+.1f}%",    trend_dir, trend_class),
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

        # ── Compute signals (needed for opportunity card) ─────────────────────
        signal_df_t2 = compute_signals(geo_df, hourly_df)
        scale_df_t2  = signal_df_t2[signal_df_t2["Action"] == "SCALE"].sort_values("_roi", ascending=False)

        # ── Current Opportunity card ──────────────────────────────────────────
        if not scale_df_t2.empty:
            best_opp = scale_df_t2.iloc[0]
            st.markdown(f"""
            <div class='opp-card'>
              <div class='opp-title'>🚀 Current Best Opportunity</div>
              <div class='opp-country'>{best_opp["Country"]}</div>
              <div class='opp-sub'>{best_opp["Window"]} · Local time {best_opp["Local Time"]} · CAC {best_opp["CAC"]}</div>
              <div class='opp-roi'>{best_opp["ROI"]} ROI</div>
              <div class='opp-sub' style='margin-top:0.5rem;font-size:0.8rem;opacity:0.7'>{best_opp["Reason"]}</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — HOURLY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with main_tab3:
    if not _files_ready:
        _upload_gate_inline()
    else:
        chart_col1, chart_col2 = st.columns([3, 2])
        with chart_col1:
            st.caption("CAC vs Conversions by Hour")
            st.plotly_chart(chart_hourly_cac_subs(hourly_df), use_container_width=True, config={"displayModeBar": False})
        with chart_col2:
            st.caption("Spend by Hour (🟢 Efficient · 🟡 Normal · 🔴 Costly)")
            st.plotly_chart(chart_hourly_spend(hourly_df), use_container_width=True, config={"displayModeBar": False})

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Raw Hourly Data")
        st.dataframe(hourly_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — GEO SIGNALS
# ══════════════════════════════════════════════════════════════════════════════
with main_tab4:
    if not _files_ready:
        _upload_gate_inline()
    else:
        signal_df = compute_signals(geo_df, hourly_df)
        scale_df  = signal_df[signal_df["Action"] == "SCALE"].sort_values("_roi", ascending=False)
        reduce_df = signal_df[signal_df["Action"] == "REDUCE"].sort_values("_spend", ascending=False)

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

        geo_tab1, geo_tab2, geo_tab3 = st.tabs(["🎯 Signal Table", "🫧 CAC vs ROI Map", "📋 Raw GEO Data"])

        with geo_tab1:
            display_cols = ["Country","Local Time","Window","Spend","Subs","CAC","ROI","CPM","CR-to-Start","Action","Reason"]
            display_df   = signal_df[[c for c in display_cols if c in signal_df.columns]].copy()

            def color_action_row(row):
                styles = {"SCALE":"background-color:#F0FBF4","WATCH":"background-color:#FFFBEE",
                          "REDUCE":"background-color:#FFF5F5","OK":""}
                s = styles.get(row.get("Action","OK"),"")
                return [s]*len(row)

            st.dataframe(display_df.style.apply(color_action_row, axis=1),
                         use_container_width=True, hide_index=True)

        with geo_tab2:
            st.caption("Bubble size = Spend. X = CAC ($). Y = ROI (%). Color = Signal.")
            st.plotly_chart(chart_geo_cac_bubble(signal_df), use_container_width=True, config={"displayModeBar": False})

        with geo_tab3:
            st.dataframe(geo_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 5 — STRATEGIC VERDICT
# ══════════════════════════════════════════════════════════════════════════════
with main_tab5:
    if not _files_ready:
        _upload_gate_inline()
    else:
        # Need these from tab 2/4 — recompute if needed
        if 'signal_df' not in dir() or signal_df is None:
            signal_df = compute_signals(geo_df, hourly_df)
            scale_df  = signal_df[signal_df["Action"] == "SCALE"].sort_values("_roi", ascending=False)
            reduce_df = signal_df[signal_df["Action"] == "REDUCE"].sort_values("_spend", ascending=False)

        if 'avg_cac' not in dir() or avg_cac == 0:
            def _gt(key, fallback):
                return hourly_grand_total.get(key, fallback)
            avg_cac = _gt("cac", 0)
            avg_cr  = _gt("cr",  0)
            last3   = hourly_df.tail(3)
            last3_avg_cac = last3["cac"].mean() if "cac" in last3.columns else 0
            trend_pct = ((last3_avg_cac - avg_cac) / avg_cac * 100) if avg_cac else 0

        # ── Signal bullets ────────────────────────────────────────────────────
        bullets = []

        if "cac" in hourly_df.columns and not hourly_df.empty:
            bh = hourly_df.loc[hourly_df["cac"].idxmin()]
            bullets.append(
                f"⭐ <b>Star Hour H{int(bh['hour'])}</b>: CAC <b>${bh['cac']:.0f}</b> — "
                f"<b>{((avg_cac - bh['cac'])/avg_cac*100):.0f}%</b> below daily avg. "
                f"Protect budget availability for this window."
            )
        if "cac" in hourly_df.columns and not hourly_df.empty:
            wh = hourly_df.loc[hourly_df["cac"].idxmax()]
            bullets.append(
                f"🔴 <b>Waste Alert H{int(wh['hour'])}</b>: CAC <b>${wh['cac']:.0f}</b> "
                f"({((wh['cac'] - avg_cac)/avg_cac*100):.0f}% above avg) on ${wh['spend']:.0f} spend. "
                f"Apply dayparting or bid caps to this slot."
            )
        if not scale_df.empty:
            top = scale_df.iloc[0]
            bullets.append(
                f"🚀 <b>Scale → {top['Country']}</b>: ROI {top['ROI']} · CAC {top['CAC']} · {top['Window']}. "
                f"Shift freed budget here immediately."
            )
        if not reduce_df.empty:
            top_r = reduce_df.iloc[0]
            bullets.append(f"🛑 <b>Cut → {top_r['Country']}</b>: {top_r['Reason']}")

        high_cpm = signal_df[signal_df["Action"] == "WATCH"]
        if not high_cpm.empty:
            countries = ", ".join(high_cpm["Country"].tolist())
            bullets.append(f"⚠️ <b>Creative Fatigue Risk</b> — {countries}: CPM above $6. Refresh ad creatives.")

        if "cac" in hourly_df.columns and len(hourly_df) >= 3:
            bullets.append(
                f"📊 <b>Last-3h CAC Trend</b>: {trend_pct:+.1f}% vs daily avg "
                f"({'improving ✅' if trend_pct < 0 else 'worsening ❌'})."
            )

        for b in bullets:
            st.markdown(f"<div class='insight-box'>{b}</div>", unsafe_allow_html=True)

        # ── Verdict Engine ────────────────────────────────────────────────────
        score = 0
        score_notes = []
        W_CAC_TREND = 3; W_SCALE_GEOS = 2; W_REDUCE_GEOS = 2; W_WATCH_GEOS = 1
        W_CAC_LEVEL = 2; W_CR_LEVEL = 1
        BLENDED_CAC_BENCHMARK = 80

        if trend_pct < -10:
            score += W_CAC_TREND * 2
            score_notes.append(f"+{W_CAC_TREND*2} CAC trend strongly improving ({trend_pct:+.1f}%)")
        elif trend_pct < 0:
            score += W_CAC_TREND
            score_notes.append(f"+{W_CAC_TREND} CAC trend improving ({trend_pct:+.1f}%)")
        elif trend_pct > 20:
            score -= W_CAC_TREND * 2
            score_notes.append(f"-{W_CAC_TREND*2} CAC trend sharply worsening ({trend_pct:+.1f}%)")
        else:
            score -= W_CAC_TREND
            score_notes.append(f"-{W_CAC_TREND} CAC trend worsening ({trend_pct:+.1f}%)")

        if avg_cac < BLENDED_CAC_BENCHMARK * 0.8:
            score += W_CAC_LEVEL * 2
            score_notes.append(f"+{W_CAC_LEVEL*2} Avg CAC ${avg_cac:.0f} well below benchmark ${BLENDED_CAC_BENCHMARK}")
        elif avg_cac < BLENDED_CAC_BENCHMARK:
            score += W_CAC_LEVEL
            score_notes.append(f"+{W_CAC_LEVEL} Avg CAC ${avg_cac:.0f} below benchmark")
        elif avg_cac < BLENDED_CAC_BENCHMARK * 1.25:
            score -= W_CAC_LEVEL
            score_notes.append(f"-{W_CAC_LEVEL} Avg CAC ${avg_cac:.0f} above benchmark")
        else:
            score -= W_CAC_LEVEL * 2
            score_notes.append(f"-{W_CAC_LEVEL*2} Avg CAC ${avg_cac:.0f} significantly above benchmark")

        golden_scales = signal_df[
            (signal_df["Action"] == "SCALE") & (signal_df["Window"].str.contains("Golden", na=False))
        ]
        n_golden = len(golden_scales)
        if n_golden > 0:
            pts = min(n_golden * W_SCALE_GEOS, 8)
            score += pts
            score_notes.append(f"+{pts} {n_golden} GEOs in active golden window with SCALE signal")

        n_reduce_v = len(reduce_df)
        if n_reduce_v > 0:
            pts = min(n_reduce_v * W_REDUCE_GEOS, 6)
            score -= pts
            score_notes.append(f"-{pts} {n_reduce_v} GEOs flagged REDUCE (waste detected)")

        n_watch = len(signal_df[signal_df["Action"] == "WATCH"])
        if n_watch > 0:
            score -= n_watch * W_WATCH_GEOS
            score_notes.append(f"-{n_watch * W_WATCH_GEOS} {n_watch} GEOs with high CPM / fatigue risk")

        if avg_cr > 0.8:
            score += W_CR_LEVEL
            score_notes.append(f"+{W_CR_LEVEL} CR {avg_cr:.2f}% above 0.8% threshold")
        elif avg_cr < 0.4:
            score -= W_CR_LEVEL
            score_notes.append(f"-{W_CR_LEVEL} CR {avg_cr:.2f}% below 0.4% — funnel underperforming")

        if score >= 6:
            verdict_emoji = "🟢"; verdict_label = "SCALE UP"
            verdict_color = "#2A7A4B"; verdict_bg = "#D6F0E0"
            verdict_text = (
                f"Signals are strongly bullish. Multiple GEOs are in golden windows with efficient CAC, "
                f"and the recent trend is improving. Increase daily budgets by <b>20–40%</b>, "
                f"prioritise top SCALE GEOs, and reallocate away from REDUCE markets."
            )
        elif score >= 2:
            verdict_emoji = "🟡"; verdict_label = "HOLD & OPTIMISE"
            verdict_color = "#7A5A00"; verdict_bg = "#FFF3CD"
            verdict_text = (
                f"Mixed signals. Do <b>not</b> increase total budget — redistribute: cut REDUCE GEOs, "
                f"push more to SCALE GEOs, and apply dayparting to the worst-performing hours."
            )
        elif score >= -2:
            verdict_emoji = "🟠"; verdict_label = "CAUTION — HOLD"
            verdict_color = "#8B4000"; verdict_bg = "#FFE9CC"
            verdict_text = (
                f"Signals are slightly bearish. Freeze any budget increases. Prioritise creative refresh "
                f"and bid cap implementation before considering any scale."
            )
        else:
            verdict_emoji = "🔴"; verdict_label = "SCALE DOWN"
            verdict_color = "#8B1A1A"; verdict_bg = "#FFE0E0"
            verdict_text = (
                f"Multiple bearish signals. <b>Reduce total budget by 20–30%</b>, pause REDUCE GEOs, "
                f"implement strict dayparting, and audit creatives for fatigue before any re-scale."
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:{verdict_bg};border:2px solid {verdict_color};border-radius:20px;padding:1.5rem 2rem;margin-top:0.5rem">
          <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.8rem">
            <span style="font-size:1.8rem">{verdict_emoji}</span>
            <div>
              <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:{verdict_color};opacity:0.8">Overall Verdict</div>
              <div style="font-size:1.6rem;font-weight:800;color:{verdict_color};line-height:1">{verdict_label}</div>
            </div>
            <div style="margin-left:auto;background:{verdict_color};color:white;border-radius:999px;padding:0.3rem 1rem;font-size:0.85rem;font-weight:700">
              Score: {score:+d}
            </div>
          </div>
          <div style="font-size:0.9rem;color:{verdict_color};line-height:1.6;margin-bottom:1rem">{verdict_text}</div>
          <details>
            <summary style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:{verdict_color};opacity:0.7;cursor:pointer">
              Score breakdown ({len(score_notes)} signals)
            </summary>
            <div style="margin-top:0.6rem">
              {"".join(f'<div style="font-size:0.78rem;color:{verdict_color};padding:0.15rem 0;opacity:0.85">· {n}</div>' for n in score_notes)}
            </div>
          </details>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 6 — MARKETING CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
with main_tab6:
    import json
    from datetime import date, timedelta
    import calendar as cal_lib
    import sqlite3 as _sqlite3
    import pathlib as _pathlib

    # ── SQLite persistent storage ─────────────────────────────────────────────
    # DB file lives next to app.py — persists across browser refreshes and
    # Streamlit Cloud restarts (note: resets on a fresh redeploy from git).
    _DB_PATH = _pathlib.Path(__file__).parent / "calendar_events.db"

    def _db_connect():
        conn = _sqlite3.connect(str(_DB_PATH), check_same_thread=False)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                date     TEXT    NOT NULL,
                name     TEXT    NOT NULL,
                country  TEXT    NOT NULL,
                flag     TEXT    DEFAULT '',
                color    TEXT    DEFAULT '#4A90D9',
                source   TEXT    DEFAULT 'manual',
                category TEXT    DEFAULT '',
                platform TEXT    DEFAULT '',
                impact   TEXT    DEFAULT '',
                notes    TEXT    DEFAULT ''
            )
        """)
        # Add new columns to existing DB if upgrading from old schema
        existing_cols = [r[1] for r in conn.execute("PRAGMA table_info(events)").fetchall()]
        for col, dtype in [("category","TEXT"), ("platform","TEXT"), ("impact","TEXT"), ("notes","TEXT")]:
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE events ADD COLUMN {col} {dtype} DEFAULT ''")
        conn.commit()
        return conn

    def _db_load_events() -> list[dict]:
        conn = _db_connect()
        rows = conn.execute(
            "SELECT id, date, name, country, flag, color, source, "
            "       COALESCE(category,''), COALESCE(platform,''), "
            "       COALESCE(impact,''), COALESCE(notes,'') "
            "FROM events ORDER BY date ASC"
        ).fetchall()
        conn.close()
        return [
            {"id": r[0], "date": r[1], "name": r[2], "country": r[3],
             "flag": r[4], "color": r[5], "source": r[6],
             "category": r[7], "platform": r[8], "impact": r[9], "notes": r[10]}
            for r in rows
        ]

    def _db_add_event(ev: dict):
        conn = _db_connect()
        conn.execute(
            "INSERT INTO events (date, name, country, flag, color, source, category, platform, impact, notes) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (ev["date"], ev["name"], ev["country"], ev.get("flag",""), ev.get("color","#4A90D9"),
             ev.get("source","manual"), ev.get("category",""), ev.get("platform",""),
             ev.get("impact",""), ev.get("notes",""))
        )
        conn.commit()
        conn.close()

    def _db_delete_where(condition_sql: str, params: tuple = ()):
        conn = _db_connect()
        conn.execute(f"DELETE FROM events WHERE {condition_sql}", params)
        conn.commit()
        conn.close()

    def _db_clear_all():
        conn = _db_connect()
        conn.execute("DELETE FROM events")
        conn.commit()
        conn.close()

    # Load from DB into session state on first run (or after rerun)
    if "cal_events_loaded" not in st.session_state:
        st.session_state["cal_events"] = _db_load_events()
        st.session_state["cal_events_loaded"] = True

    # ── Country list for the dropdown ─────────────────────────────────────────
    CAL_COUNTRIES = [
        "United States", "United Arab Emirates", "Austria", "Australia",
        "Belgium", "Bulgaria", "Canada", "Switzerland", "Chile", "Colombia",
        "Costa Rica", "Czech Republic", "Germany", "Denmark", "Dominican Republic",
        "Ecuador", "Estonia", "Spain", "Finland", "France", "United Kingdom",
        "Greece", "Croatia", "Hungary", "Indonesia", "Ireland", "Israel",
        "Italy", "Jordan", "South Korea", "Kuwait", "Lithuania", "Latvia",
        "Morocco", "Mexico", "Malaysia", "Netherlands", "New Zealand", "Oman",
        "Panama", "Poland", "Portugal", "Qatar", "Romania", "Serbia",
        "Saudi Arabia", "Singapore", "Slovenia", "Slovakia", "Sweden",
        "Thailand", "Turkey", "Taiwan", "South Africa",
    ]

    CAL_COUNTRY_ISO = {
        "United States":"US","United Arab Emirates":"AE","Austria":"AT",
        "Australia":"AU","Belgium":"BE","Bulgaria":"BG","Canada":"CA",
        "Switzerland":"CH","Chile":"CL","Colombia":"CO","Costa Rica":"CR",
        "Czech Republic":"CZ","Germany":"DE","Denmark":"DK",
        "Dominican Republic":"DO","Ecuador":"EC","Estonia":"EE","Spain":"ES",
        "Finland":"FI","France":"FR","United Kingdom":"GB","Greece":"GR",
        "Croatia":"HR","Hungary":"HU","Indonesia":"ID","Ireland":"IE",
        "Israel":"IL","Italy":"IT","Jordan":"JO","South Korea":"KR",
        "Kuwait":"KW","Lithuania":"LT","Latvia":"LV","Morocco":"MA",
        "Mexico":"MX","Malaysia":"MY","Netherlands":"NL","New Zealand":"NZ",
        "Oman":"OM","Panama":"PA","Poland":"PL","Portugal":"PT","Qatar":"QA",
        "Romania":"RO","Serbia":"RS","Saudi Arabia":"SA","Singapore":"SG",
        "Slovenia":"SI","Slovakia":"SK","Sweden":"SE","Thailand":"TH",
        "Turkey":"TR","Taiwan":"TW","South Africa":"ZA",
    }

    CAL_COUNTRY_FLAG = {
        "United States":"🇺🇸","United Arab Emirates":"🇦🇪","Austria":"🇦🇹",
        "Australia":"🇦🇺","Belgium":"🇧🇪","Bulgaria":"🇧🇬","Canada":"🇨🇦",
        "Switzerland":"🇨🇭","Chile":"🇨🇱","Colombia":"🇨🇴","Costa Rica":"🇨🇷",
        "Czech Republic":"🇨🇿","Germany":"🇩🇪","Denmark":"🇩🇰",
        "Dominican Republic":"🇩🇴","Ecuador":"🇪🇨","Estonia":"🇪🇪",
        "Spain":"🇪🇸","Finland":"🇫🇮","France":"🇫🇷","United Kingdom":"🇬🇧",
        "Greece":"🇬🇷","Croatia":"🇭🇷","Hungary":"🇭🇺","Indonesia":"🇮🇩",
        "Ireland":"🇮🇪","Israel":"🇮🇱","Italy":"🇮🇹","Jordan":"🇯🇴",
        "South Korea":"🇰🇷","Kuwait":"🇰🇼","Lithuania":"🇱🇹","Latvia":"🇱🇻",
        "Morocco":"🇲🇦","Mexico":"🇲🇽","Malaysia":"🇲🇾","Netherlands":"🇳🇱",
        "New Zealand":"🇳🇿","Oman":"🇴🇲","Panama":"🇵🇦","Poland":"🇵🇱",
        "Portugal":"🇵🇹","Qatar":"🇶🇦","Romania":"🇷🇴","Serbia":"🇷🇸",
        "Saudi Arabia":"🇸🇦","Singapore":"🇸🇬","Slovenia":"🇸🇮","Slovakia":"🇸🇰",
        "Sweden":"🇸🇪","Thailand":"🇹🇭","Turkey":"🇹🇷","Taiwan":"🇹🇼",
        "South Africa":"🇿🇦",
    }

    # Color palette for events
    EVENT_COLORS = {
        "🟥 Red":     "#E05252",
        "🟧 Orange":  "#F0A500",
        "🟨 Yellow":  "#F5D000",
        "🟩 Green":   "#4CAF72",
        "🟦 Blue":    "#4A90D9",
        "🟪 Purple":  "#9B6DD8",
        "⬜ Beige":   "#DDD5CC",
        "⬛ Dark":    "#3B2F25",
    }

    # ── Helper: load holidays into calendar events ────────────────────────────
    def load_country_holidays_to_cal(country: str, year: int) -> list[dict]:
        """Fetch all public holidays for a country/year and return as event dicts."""
        import holidays as hol_lib2
        iso2 = CAL_COUNTRY_ISO.get(country)
        if not iso2:
            return []
        try:
            h = hol_lib2.country_holidays(iso2, years=year)
            try:
                if "en_US" in h.supported_languages:
                    h = hol_lib2.country_holidays(iso2, years=year, language="en_US")
            except Exception:
                pass
            flag = CAL_COUNTRY_FLAG.get(country, "")
            color = "#4A90D9"  # default blue for auto-loaded holidays
            events = []
            for d, name in sorted(h.items()):
                events.append({
                    "date":    d.isoformat(),
                    "name":    name,
                    "country": country,
                    "flag":    flag,
                    "color":   color,
                    "source":  "auto",
                })
            return events
        except Exception:
            return []

    # ── Controls ──────────────────────────────────────────────────────────────
    now_cal = datetime.now(pytz.utc)
    cal_ctrl1, cal_ctrl2 = st.columns([5, 3])

    with cal_ctrl2:

        # ── 1. ADD MANUAL EVENT ───────────────────────────────────────────────
        st.markdown("### ➕ Add Event")
        with st.form("add_event_form", clear_on_submit=True):
            ev_country   = st.selectbox("Country", CAL_COUNTRIES, key="ev_country")
            ev_name      = st.text_input("Event name", placeholder="e.g. Black Friday, Campaign Launch")
            ev_date      = st.date_input("Date", value=now_cal.date())
            ev_color_lbl = st.selectbox("Color", list(EVENT_COLORS.keys()))
            ev_color     = EVENT_COLORS[ev_color_lbl]
            submitted    = st.form_submit_button("Add to Calendar", use_container_width=True)
            if submitted and ev_name:
                _db_add_event({
                    "date":    ev_date.isoformat(),
                    "name":    ev_name,
                    "country": ev_country,
                    "flag":    CAL_COUNTRY_FLAG.get(ev_country, ""),
                    "color":   ev_color,
                    "source":  "manual",
                })
                st.session_state["cal_events"] = _db_load_events()
                st.success(f"✅ Saved: {ev_name} on {ev_date}")

        st.markdown("---")

        # ── 2. LOAD PUBLIC HOLIDAYS — checkboxes, no dropdown ─────────────────
        st.markdown("### 🗺️ Load Public Holidays")
        hl_year = st.selectbox(
            "Year", [now_cal.year, now_cal.year + 1],
            key="hl_year_select",
            label_visibility="visible"
        )

        # Which countries already have auto-holidays loaded for this year?
        already_loaded = set(
            e["country"] for e in st.session_state["cal_events"]
            if e["source"] == "auto" and e["date"].startswith(str(hl_year))
        )

        st.caption("Check to load · Uncheck to remove from calendar (data stays in DB)")

        # Scroll container for the country checklist
        checkbox_container = st.container(height=260)
        with checkbox_container:
            for country in CAL_COUNTRIES:
                is_checked = country in already_loaded
                new_state  = st.checkbox(
                    f"{CAL_COUNTRY_FLAG.get(country, '')} {country}",
                    value=is_checked,
                    key=f"hl_chk_{country}_{hl_year}"
                )
                if new_state and not is_checked:
                    # User just checked → load holidays into DB
                    new_events = load_country_holidays_to_cal(country, hl_year)
                    _db_delete_where(
                        "country=? AND source='auto' AND date LIKE ?",
                        (country, f"{hl_year}%")
                    )
                    for ev in new_events:
                        _db_add_event(ev)
                    st.session_state["cal_events"] = _db_load_events()
                    st.rerun()
                elif not new_state and is_checked:
                    # User just unchecked → remove from DB (but seeded events stay)
                    _db_delete_where(
                        "country=? AND source='auto' AND date LIKE ?",
                        (country, f"{hl_year}%")
                    )
                    st.session_state["cal_events"] = _db_load_events()
                    st.rerun()

        st.markdown("---")

        # ── 3. VISIBILITY FILTER — hide/show without deleting ─────────────────
        # Uses session state so nothing is ever deleted from the DB
        all_cal_countries = sorted(set(e["country"] for e in st.session_state["cal_events"]))

        if "cal_hidden" not in st.session_state:
            st.session_state["cal_hidden"] = set()   # set of hidden country/platform names

        st.markdown("### 👁️ Show / Hide")
        st.caption("Toggle visibility. Events are never deleted.")

        if all_cal_countries:
            # Quick actions
            qc1, qc2 = st.columns(2)
            with qc1:
                if st.button("Show All", use_container_width=True, key="show_all_btn"):
                    st.session_state["cal_hidden"] = set()
                    st.rerun()
            with qc2:
                if st.button("Hide All", use_container_width=True, key="hide_all_btn"):
                    st.session_state["cal_hidden"] = set(all_cal_countries)
                    st.rerun()

            vis_container = st.container(height=180)
            with vis_container:
                for country in all_cal_countries:
                    currently_hidden = country in st.session_state["cal_hidden"]
                    visible = st.checkbox(
                        country,
                        value=not currently_hidden,
                        key=f"vis_{country}"
                    )
                    if visible and currently_hidden:
                        st.session_state["cal_hidden"].discard(country)
                        st.rerun()
                    elif not visible and not currently_hidden:
                        st.session_state["cal_hidden"].add(country)
                        st.rerun()
        else:
            st.caption("No events loaded yet.")

        # cal_filter_countries = what's actually visible
        cal_filter_countries = [
            c for c in all_cal_countries
            if c not in st.session_state.get("cal_hidden", set())
        ]

        st.markdown("---")

        # ── 4. DELETE MANUAL EVENTS ONLY ──────────────────────────────────────
        st.markdown("### 🗑️ Delete")
        st.caption("Only manually added events can be deleted.")
        if st.button("Delete all manual events", use_container_width=True, key="del_manual_btn"):
            _db_delete_where("source='manual'")
            st.session_state["cal_events"] = _db_load_events()
            st.rerun()

    # ── Main calendar view ────────────────────────────────────────────────────
    with cal_ctrl1:
        # Month navigation
        if "cal_year"  not in st.session_state: st.session_state["cal_year"]  = now_cal.year
        if "cal_month" not in st.session_state: st.session_state["cal_month"] = now_cal.month

        nav1, nav2, nav3, nav4 = st.columns([1, 2, 2, 1])
        with nav1:
            if st.button("◀", key="prev_month"):
                if st.session_state["cal_month"] == 1:
                    st.session_state["cal_month"] = 12
                    st.session_state["cal_year"] -= 1
                else:
                    st.session_state["cal_month"] -= 1
                st.rerun()
        with nav2:
            import calendar as cal_lib
            month_name = cal_lib.month_name[st.session_state["cal_month"]]
            st.markdown(
                f"<div style='font-size:1.3rem;font-weight:700;color:#3B2F25;padding-top:0.3rem'>"
                f"{month_name} {st.session_state['cal_year']}</div>",
                unsafe_allow_html=True
            )
        with nav3:
            if st.button("Today", key="today_btn"):
                st.session_state["cal_year"]  = now_cal.year
                st.session_state["cal_month"] = now_cal.month
                st.rerun()
        with nav4:
            if st.button("▶", key="next_month"):
                if st.session_state["cal_month"] == 12:
                    st.session_state["cal_month"] = 1
                    st.session_state["cal_year"] += 1
                else:
                    st.session_state["cal_month"] += 1
                st.rerun()

        # Build event lookup: {date_str: [event, ...]}
        active_events = [
            e for e in st.session_state["cal_events"]
            if e["country"] in cal_filter_countries
        ] if cal_filter_countries else st.session_state["cal_events"]
        event_map: dict[str, list] = {}
        for ev in active_events:
            event_map.setdefault(ev["date"], []).append(ev)

        # Build calendar grid
        view_year  = st.session_state["cal_year"]
        view_month = st.session_state["cal_month"]
        today_date = now_cal.date()

        # Day headers
        day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        header_cols = st.columns(7)
        for i, dh in enumerate(day_headers):
            with header_cols[i]:
                color = "#E05252" if dh in ("Sat", "Sun") else "#8B7355"
                st.markdown(
                    f"<div style='text-align:center;font-size:0.72rem;font-weight:700;"
                    f"letter-spacing:0.06em;text-transform:uppercase;color:{color};"
                    f"padding-bottom:0.4rem;border-bottom:2px solid #DDD5CC'>{dh}</div>",
                    unsafe_allow_html=True
                )

        # Get month calendar matrix (Mon-start)
        cal_matrix = cal_lib.monthcalendar(view_year, view_month)

        for week in cal_matrix:
            week_cols = st.columns(7)
            for col_i, day_num in enumerate(week):
                with week_cols[col_i]:
                    if day_num == 0:
                        st.markdown(
                            "<div style='min-height:90px;background:#F7F3EE;border-radius:10px;margin:2px'></div>",
                            unsafe_allow_html=True
                        )
                    else:
                        cell_date = date(view_year, view_month, day_num)
                        date_str  = cell_date.isoformat()
                        is_today  = (cell_date == today_date)
                        is_weekend = col_i >= 5

                        day_events = event_map.get(date_str, [])

                        # Build event pills HTML (max 3 shown, +N if more)
                        ev_html = ""
                        for ev in day_events[:3]:
                            c = ev["color"]
                            flag = ev.get("flag", "")
                            name_short = ev["name"][:18] + ("…" if len(ev["name"]) > 18 else "")
                            ev_html += (
                                f"<div style='background:{c};color:white;border-radius:5px;"
                                f"padding:1px 5px;font-size:0.62rem;font-weight:600;"
                                f"margin-top:2px;white-space:nowrap;overflow:hidden;"
                                f"text-overflow:ellipsis' title='{ev["name"]} — {ev["country"]}'>"
                                f"{flag} {name_short}</div>"
                            )
                        if len(day_events) > 3:
                            ev_html += f"<div style='font-size:0.6rem;color:#8B7355;margin-top:2px'>+{len(day_events)-3} more</div>"

                        # Cell styling
                        bg    = "#3B2F25" if is_today else ("#FFF8F8" if is_weekend else "#F0EAE1")
                        num_c = "white"   if is_today else ("#E05252" if is_weekend else "#3B2F25")
                        border = "2px solid #3B2F25" if is_today else "1px solid #DDD5CC"

                        st.markdown(
                            f"<div style='min-height:90px;background:{bg};border:{border};"
                            f"border-radius:10px;padding:6px 7px;margin:2px'>"
                            f"<div style='font-size:0.82rem;font-weight:700;color:{num_c}'>{day_num}</div>"
                            f"{ev_html}"
                            f"</div>",
                            unsafe_allow_html=True
                        )

        # ── Event list below calendar ─────────────────────────────────────────
        if active_events:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<p class='section-header'>📋 All Events This View ({view_month}/{view_year})</p>",
                unsafe_allow_html=True
            )
            month_events = sorted(
                [e for e in active_events if e["date"].startswith(f"{view_year}-{view_month:02d}")],
                key=lambda x: x["date"]
            )
            if month_events:
                for ev in month_events:
                    ev_date_fmt = datetime.strptime(ev["date"], "%Y-%m-%d").strftime("%a %b %d")
                    flag = ev.get("flag", "")
                    dot = f"<span style='display:inline-block;width:10px;height:10px;background:{ev['color']};border-radius:50%;margin-right:6px'></span>"
                    # Source badge
                    if ev["source"] == "seeded":
                        src_badge = "<span style='background:#EEF0FF;font-size:0.6rem;padding:1px 6px;border-radius:8px;color:#4A5499'>seeded</span>"
                    elif ev["source"] == "auto":
                        src_badge = "<span style='background:#EAE4DC;font-size:0.6rem;padding:1px 6px;border-radius:8px;color:#8B7355'>auto</span>"
                    else:
                        src_badge = "<span style='background:#D6F0E0;font-size:0.6rem;padding:1px 6px;border-radius:8px;color:#2A7A4B'>manual</span>"
                    # Impact badge
                    impact = ev.get("impact", "")
                    imp_colors = {"high": ("#FFE0E0","#8B1A1A"), "med": ("#FFF3CD","#7A5A00"), "low": ("#F0EAE1","#8B7355")}
                    ibg, ifc = imp_colors.get(impact, ("#F0EAE1","#8B7355"))
                    imp_badge = f"<span style='background:{ibg};color:{ifc};font-size:0.6rem;padding:1px 6px;border-radius:8px;font-weight:600'>{impact}</span>" if impact else ""
                    # Category
                    cat = ev.get("category", "")
                    cat_badge = f"<span style='font-size:0.6rem;color:#8B7355;padding:1px 6px;border-radius:8px;background:#F7F3EE'>{cat}</span>" if cat else ""
                    notes = ev.get("notes", "")
                    notes_html = f"<div style='font-size:0.72rem;color:#8B7355;margin-top:2px;padding-left:16px'>{notes[:120]}{'…' if len(notes)>120 else ''}</div>" if notes else ""
                    st.markdown(
                        f"<div style='padding:0.4rem 0.6rem;border-bottom:1px solid #EDE6DC'>"
                        f"<div style='display:flex;align-items:center;gap:0.4rem;font-size:0.82rem'>"
                        f"{dot}<b style='color:#3B2F25;min-width:85px'>{ev_date_fmt}</b>"
                        f"<span>{flag} {ev['country']}</span>"
                        f"<span style='color:#3B2F25;flex:1;font-weight:500'>{ev['name']}</span>"
                        f"{imp_badge} {cat_badge} {src_badge}"
                        f"</div>{notes_html}</div>",
                        unsafe_allow_html=True
                    )
            else:
                st.caption("No events this month.")


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;font-size:0.72rem;color:#8B7355;padding:1rem 0;border-top:1px solid #DDD5CC'>"
    "Dressly UA Dashboard · Built for Media Buyers · Holidays auto-update each year via Python holidays library"
    "</div>",
    unsafe_allow_html=True,
)
