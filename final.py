import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import time
import base64

# --- constants --------------------------------------------------------------
SECONDS_PER_DAY     = 24 * 60 * 60
UPDATE_INTERVAL_SEC = 2
TZ                  = ZoneInfo("America/Los_Angeles")

# --- ONLY PLASTIC-RELATED CONSTANTS ---
TOTAL_DAILY_PLASTIC_KG = 1_260_273_973
PLASTIC_KG_PER_SECOND = TOTAL_DAILY_PLASTIC_KG / SECONDS_PER_DAY

TOTAL_DAILY_OCEAN_PLASTIC_KG = 30_136_986
OCEAN_PLASTIC_KG_PER_SECOND = TOTAL_DAILY_OCEAN_PLASTIC_KG / SECONDS_PER_DAY

TOTAL_DAILY_MICROPLASTIC_MG = 714.0
MICROPLASTIC_MG_PER_SECOND = TOTAL_DAILY_MICROPLASTIC_MG / SECONDS_PER_DAY


# --- Font Loader (kept as it's a styling utility) ---------------------------
def load_woff_font_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# --- helper functions ------------------------------------------------------

def time_elapsed_seconds(now: datetime) -> float:
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elapsed = (now - midnight).total_seconds()
    return max(0, min(elapsed, SECONDS_PER_DAY))

def format_elapsed_hours(seconds: float) -> str:
    hours = int(seconds // 3600)
    return f"Running Time: {hours} hours"

# --- ONLY PLASTIC-RELATED CALCULATION FUNCTIONS ---
def plastic_produced_so_far(now: datetime) -> float:
    return PLASTIC_KG_PER_SECOND * time_elapsed_seconds(now)

def ocean_plastic_entered_so_far(now: datetime) -> float:
    return OCEAN_PLASTIC_KG_PER_SECOND * time_elapsed_seconds(now)

def microplastic_ingested_so_far(now: datetime) -> float:
    return MICROPLASTIC_MG_PER_SECOND * time_elapsed_seconds(now)

def k_format(val: float) -> str:
    if val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.1f}B".rstrip('0').rstrip('.')
    elif val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M".rstrip('0').rstrip('.')
    elif val >= 1_000:
        return f"{val / 1_000:.0f}k"
    else:
        return f"{val:,.0f}"


# --- Streamlit app main -----------------------------------------------------

def main():
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

    try:
        qartella_font = load_woff_font_base64("Qartella.woff")
        st.markdown(f"""
            <style>
            @font-face {{
                font-family: 'Qartella';
                src: url(data:font/woff;base64,{qartella_font}) format('woff');
                font-weight: normal;
                font-style: normal;
            }}

            html, body, [class*="st-"] {{
                font-family: 'Qartella', serif !important;
            }}

            .stApp {{
                background-color: #0E1117;
                color: white;
            }}

            .metric-block {{
                margin-bottom: 0px;
                text-align: center; /* This centers the text within the metric-block div */
            }}
            .metric-label {{
                color: white;
                font-size: 1.5em;
                margin-bottom: 5px;
                white-space: nowrap;
            }}
            .metric-value {{
                color: white;
                font-size: 3em;
                font-weight: bold;
                margin-bottom: 5px;
                white-space: nowrap;
            }}
            .metric-comparison {{
                color: #70c38B;
                font-size: 1.8em;
                margin-top: 0px;
                white-space: nowrap;
            }}
            .bottom-left {{
                font-size: 1.1em;
                font-weight: bold;
                margin-top: 60px;
                text-align: center;
                width: 100%;
            }}
            
            /* Target Streamlit's column divs to ensure their content is centered */
            /* Streamlit columns are typically flex containers. We want to align items in the cross-axis. */
            div[data-testid="stColumn"] {{
                display: flex;
                flex-direction: column; /* Stack children vertically */
                align-items: center;   /* Center horizontally within the column */
                justify-content: flex-start; /* Align content to the top */
            }}

            /* Ensure stImage div also aligns its content */
            div.stImage {{
                display: flex;
                justify-content: center; /* Center image horizontally */
                align-items: flex-start;
                margin-top: 10px;
                margin-bottom: 0px;
            }}
            </style>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Qartella.woff font file not found. Using default font.")
        st.markdown("""
            <style>
            .stApp { background-color: #0E1117; color: white; }
            .metric-block { margin-bottom: 0px; text-align: center; }
            .metric-label { color: white; font-size: 1.5em; margin-bottom: 5px; white-space: nowrap; }
            .metric-value { color: white; font-size: 3em; font-weight: bold; margin-bottom: 5px; white-space: nowrap; }
            .metric-comparison { white-space: nowrap; }
            .bottom-left {
                font-size: 1.1em;
                font-weight: bold;
                margin-top: 60px;
                text-align: center;
                width: 100%;
            }
            div[data-testid="stColumn"] {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
            }
            div.stImage {
                display: flex;
                justify-content: center;
                align-items: flex-start;
                margin-top: 10px;
                margin-bottom: 0px;
            }
            </style>
        """, unsafe_allow_html=True)


    placeholder = st.empty()

    while True:
        now = datetime.now(TZ)
        elapsed_seconds = time_elapsed_seconds(now)
        running_hours = int(elapsed_seconds // 3600)
        running_time_str = format_elapsed_hours(elapsed_seconds)

        plastic_produced = plastic_produced_so_far(now)
        plastic_to_cars = plastic_produced / 1500

        ocean_plastic = ocean_plastic_entered_so_far(now)
        ocean_to_statues = ocean_plastic / 204116

        microplastic = microplastic_ingested_so_far(now)
        credit_card_equiv = ((microplastic * 7) / 5000) * 100

        with placeholder.container():
            # Adjusting column widths to make content columns a bit wider relative to spacers
            # This might help with perceived centering, though CSS alignment is primary
            col_widths = [0.5, 4, 1, 4, 1, 4, 0.5] # Reduced spacer width, increased content width
            
            s_left, c1, s_1_2, c2, s_2_3, c3, s_right = st.columns(col_widths)

            with c1:
                st.markdown(f"""
                    <div class="metric-block">
                        <p class="metric-label">Plastic Produced Today</p>
                        <p class="metric-value">{plastic_produced:,.0f} kg</p>
                        <p class="metric-comparison">≈{plastic_to_cars:,.0f} cars</p>
                    </div>
                """, unsafe_allow_html=True)
                st.image("Frame 18.png", width=350)

            with c2:
                st.markdown(f"""
                    <div class="metric-block">
                        <p class="metric-label">Plastic Entered Ocean Today</p>
                        <p class="metric-value">{ocean_plastic:,.0f} kg</p>
                        <p class="metric-comparison">≈{ocean_to_statues:,.0f} Statues of Liberty</p>
                    </div>
                """, unsafe_allow_html=True)
                st.image("Frame 17.png", width=350)

            with c3:
                st.markdown(f"""
                    <div class="metric-block">
                        <p class="metric-label">Microplastic Ingested Today</p>
                        <p class="metric-value">{microplastic:,.0f} mg</p>
                        <p class="metric-comparison">≈{credit_card_equiv:.1f}% credit card/week</p>
                    </div>
                """, unsafe_allow_html=True)
                st.image("Frame 20.png", width=350)

            st.markdown(f"""
                <div class="bottom-left">
                    Running Time: {running_hours} hours
                </div>
            """, unsafe_allow_html=True)

        time.sleep(UPDATE_INTERVAL_SEC)

if __name__ == "__main__":
    main()