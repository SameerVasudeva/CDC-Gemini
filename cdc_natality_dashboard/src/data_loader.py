import os
import pandas as pd
import streamlit as st

STATE_ABBR_MAP = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI',
    'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
    'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
    'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
    'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI',
    'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
    'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

REQUIRED_COLUMNS = ['state_of_residence', 'month', 'month_code', 'year_code', 'sex_of_infant', 'births']

@st.cache_data
def load_data(file_path: str = None) -> pd.DataFrame:
    """Loads and validates the CDC provisional natality dataset."""
    if file_path is None:
        possible_paths = [
            "Provisional_Natality_2025_CDC1.csv",
            "data/Provisional_Natality_2025_CDC1.csv",
            os.path.join(os.path.dirname(__file__), "..", "data", "Provisional_Natality_2025_CDC1.csv"),
            os.path.join(os.path.dirname(__file__), "..", "Provisional_Natality_2025_CDC1.csv")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
    
    if not file_path or not os.path.exists(file_path):
        st.error("Data file 'Provisional_Natality_2025_CDC1.csv' could not be found.")
        st.stop()

    df = pd.read_csv(file_path)

    # Data validation
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        st.error(f"Dataset missing required columns: {missing_cols}")
        st.stop()

    # Data transformation
    df['state_abbr'] = df['state_of_residence'].map(STATE_ABBR_MAP)
    df['month'] = pd.Categorical(
        df['month'], 
        categories=[
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ],
        ordered=True
    )
    df = df.sort_values(['month_code', 'state_of_residence'])
    return df

def filter_data(df: pd.DataFrame, selected_states: list, selected_months: list, selected_sex: str) -> pd.DataFrame:
    """Applies sidebar filter parameters to the dataset."""
    filtered_df = df.copy()

    if selected_states:
        filtered_df = filtered_df[filtered_df['state_of_residence'].isin(selected_states)]
    if selected_months:
        filtered_df = filtered_df[filtered_df['month'].isin(selected_months)]
    if selected_sex != 'All':
        filtered_df = filtered_df[filtered_df['sex_of_infant'] == selected_sex]

    return filtered_df
