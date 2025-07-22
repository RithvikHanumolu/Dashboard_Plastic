import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo   # Python 3.9+
import pandas as pd # Kept for potential future use or if other data processing is added, but not strictly used for current plastic stats
import time
import base64

# --- constants --------------------------------------------------------------
SECONDS_PER_DAY     = 24 * 60 * 60  # 86,400 seconds in a day
UPDATE_INTERVAL_SEC = 2             # update frequency (seconds)
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
    # Set page config to wide layout to allow more horizontal space
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

    # Attempt to load font, with fallback if not found
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

            /* Apply Qartella font globally */
            html, body, [class*="st-"] {{
                font-family: 'Qartella', serif !important;
            }}

            .stApp {{
                background-color: #0E1117;
                color: white;
            }}

            .metric-block {{
                margin-bottom: 0px; /* Remove space below text block */
                text-align: center; /* Center the text within the metric block */
            }}
            .metric-label {{
                color: white;
                font-size: 1.5em;
                margin-bottom: 5px;
            }}
            .metric-value {{
                color: white;
                font-size: 3em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .metric-comparison {{
                color: #70c38B;
                font-size: 1.8em;
                margin-top: 0px;
                white-space: nowrap;  /* Prevent line breaks */
                overflow: hidden; /* Hide overflow if nowrap causes it to go beyond container */
                text-overflow: ellipsis; /* Add ellipsis for overflowed text, though nowrap might make it just cut off */
            }}
            /* Adjusted .bottom-left for relative positioning, spacing, and font size */
            .bottom-left {{
                font-size: 1.1em; /* Reduced font size here */
                font-weight: bold;
                margin-top: 60px; /* Space above running time */
                text-align: center; /* Center the running time text */
                width: 100%; /* Ensure it takes full width for centering */
            }}
            /* Crucial CSS to center images within their Streamlit-generated div and align vertically */
            div.stImage {{
                display: flex; /* Use flexbox for centering content */
                justify-content: center; /* Center horizontally */
                align-items: flex-start; /* Align content to the top within the flex container */
                margin-top: -20px; /* Adjust this value to pull the image up closer to the text. Experiment! */
                margin-bottom: 0px; /* Ensure no extra space below the image */
            }}
            </style>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Qartella.woff font file not found. Using default font.")
        # Fallback CSS if font is not found (simplified for brevity)
        st.markdown("""
            <style>
            .stApp { background-color: #0E1117; color: white; }
            .metric-block { margin-bottom: 0px; text-align: center; }
            .metric-label { color: white; font-size: 1.5em; margin-bottom: 5px; }
            .metric-value { color: white; font-size: 3em; font-weight: bold; margin-bottom: 5px; }
            .metric-comparison { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .bottom-left {
                font-size: 1.1em; /* Reduced font size here */
                font-weight: bold;
                margin-top: 60px;
                text-align: center;
                width: 100%;
            }
            div.stImage {
                display: flex;
                justify-content: center;
                align-items: flex-start;
                margin-top: -20px;
                margin-bottom: 0px;
            }
            </style>
        """, unsafe_allow_html=True)


    placeholder = st.empty()

    while True:
        now = datetime.now(TZ)
        elapsed_seconds = time_elapsed_seconds(now)
        # Define running_hours here!
        running_hours = int(elapsed_seconds // 3600) # FIX: Added this line
        running_time_str = format_elapsed_hours(elapsed_seconds)

        plastic_produced = plastic_produced_so_far(now)
        plastic_to_cars = plastic_produced / 1500

        ocean_plastic = ocean_plastic_entered_so_far(now)
        ocean_to_statues = ocean_plastic / 204116

        microplastic = microplastic_ingested_so_far(now)
        credit_card_equiv = ((microplastic * 7) / 5000) * 100  # Corrected percentage

        with placeholder.container():
            # Define column widths for centering and spacing
            col_widths = [2, 3, 2, 3, 2, 3, 2]
            
            # Unpack columns: c1, c2, c3 are content columns; s1, s2, s3, s4 are spacers
            s1, c1, s2, c2, s3, c3, s4 = st.columns(col_widths)

            with c1: # Use the first content column
                st.markdown(f"""
                    <div class="metric-block">
                        <p class="metric-label">Plastic Produced Today</p>
                        <p class="metric-value">{plastic_produced:,.0f} kg</p>
                        <p class="metric-comparison">≈{plastic_to_cars:,.0f} cars</p>
                    </div>
                """, unsafe_allow_html=True)
                # IMPORTANT: Ensure this image file is in the same directory as your script
                st.image("Frame 18.png", width=350)

            with c2: # Use the second content column
                st.markdown(f"""
                    <div class="metric-block">
                        <p class="metric-label">Plastic Entered Ocean</p>
                        <p class="metric-value">{ocean_plastic:,.0f} kg</p>
                        <p class="metric-comparison">≈{ocean_to_statues:,.0f} Statues of Liberty</p>
                    </div>
                """, unsafe_allow_html=True)
                # IMPORTANT: Ensure this image file is in the same directory as your script
                st.image("Frame 17.png", width=350)

            with c3: # Use the third content column
                st.markdown(f"""
                    <div class="metric-block">
                        <p class="metric-label">Microplastic Ingested</p>
                        <p class="metric-value">{microplastic:,.0f} mg</p>
                        <p class="metric-comparison">≈{credit_card_equiv:.1f}% credit card/week</p>
                    </div>
                """, unsafe_allow_html=True)
                # IMPORTANT: Ensure this image file is in the same directory as your script
                st.image("Frame 20.png", width=350)

            # Running Time moved here and styled to be centered with margin-top
            st.markdown(f"""
                <div class="bottom-left">
                    Running Time: {running_hours} hours
                </div>
            """, unsafe_allow_html=True)

        time.sleep(UPDATE_INTERVAL_SEC)

if __name__ == "__main__":
    main()
