import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
st.set_page_config(
    page_title="CDC Provisional Natality Explorer 2025",
    page_icon="📊",
    layout="wide"
)

ACCESSIBLE_COLOR_MALE = "#1f77b4"
ACCESSIBLE_COLOR_FEMALE = "#ff7f0e"

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

# ==========================================
# DATA LOADING & FILTERING
# ==========================================
@st.cache_data
def load_data(file_name: str = "Provisional_Natality_2025_CDC1.csv") -> pd.DataFrame:
    """Loads and validates the CDC provisional natality dataset."""
    possible_paths = [
        file_name,
        os.path.join("data", file_name),
        os.path.join(os.path.dirname(__file__), file_name),
        os.path.join(os.path.dirname(__file__), "data", file_name)
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
            
    if not file_path:
        st.error(f"Data file '{file_name}' could not be found. Please ensure it is uploaded in the root or data folder.")
        st.stop()

    df = pd.read_csv(file_path)

    # Data validation
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        st.error(f"Dataset missing required columns: {missing_cols}")
        st.stop()

    # Transformations & Ordering
    df['state_abbr'] = df['state_of_residence'].map(STATE_ABBR_MAP)
    df['month'] = pd.Categorical(
        df['month'], 
        categories=[
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ],
        ordered=True
    )
    return df.sort_values(['month_code', 'state_of_residence'])

def filter_data(df: pd.DataFrame, selected_states: list, selected_months: list, selected_sex: str) -> pd.DataFrame:
    """Applies active sidebar filters to dataset."""
    filtered_df = df.copy()

    if selected_states:
        filtered_df = filtered_df[filtered_df['state_of_residence'].isin(selected_states)]
    if selected_months:
        filtered_df = filtered_df[filtered_df['month'].isin(selected_months)]
    if selected_sex != 'All':
        filtered_df = filtered_df[filtered_df['sex_of_infant'] == selected_sex]

    return filtered_df

# ==========================================
# UI COMPONENTS & LAYOUT
# ==========================================
def render_header():
    """Renders dashboard header, attribution, and notices."""
    st.title("CDC Provisional Natality Explorer (2025)")
    st.markdown(
        """
        **Audience Focus:** Undergraduate Business Analytics Exploration  
        *Data Source: Centers for Disease Control and Prevention (CDC) / NCHS Provisional Natality Data.*
        """
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.warning("⚠️ **Notice**: These data are **PROVISIONAL** and subject to future revisions by the CDC.")
    with col2:
        st.info("ℹ️ **Important Metric Note**: Figures represent **raw birth counts**, NOT population birth rates.")

def render_sidebar(df: pd.DataFrame):
    """Renders sidebar controls, multiselects, reset button, and filter summaries."""
    st.sidebar.header("Filter & Analysis Controls")

    all_states = sorted(df['state_of_residence'].unique().tolist())
    all_months = df['month'].cat.categories.tolist()
    
    if "selected_states" not in st.session_state:
        st.session_state.selected_states = all_states.copy()
    if "selected_months" not in st.session_state:
        st.session_state.selected_months = all_months.copy()
    if "selected_sex" not in st.session_state:
        st.session_state.selected_sex = "All"

    if st.sidebar.button("🔄 Reset All Filters"):
        st.session_state.selected_states = all_states.copy()
        st.session_state.selected_months = all_months.copy()
        st.session_state.selected_sex = "All"
        st.rerun()

    col_a, col_b = st.sidebar.columns(2)
    if col_a.button("Select All States"):
        st.session_state.selected_states = all_states.copy()
        st.rerun()
    if col_b.button("Clear States"):
        st.session_state.selected_states = []
        st.rerun()

    selected_states = st.sidebar.multiselect("Select Geographies:", options=all_states, key="selected_states")
    selected_months = st.sidebar.multiselect("Select Months:", options=all_months, key="selected_months")
    selected_sex = st.sidebar.radio("Infant Sex:", options=["All", "Female", "Male"], key="selected_sex")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Active Filter Summary")
    st.sidebar.caption(f"• **Geographies**: {len(selected_states)} / {len(all_states)} selected")
    st.sidebar.caption(f"• **Months**: {len(selected_months)} / {len(all_months)} selected")
    st.sidebar.caption(f"• **Infant Sex**: {selected_sex}")

    return selected_states, selected_months, selected_sex

def render_kpi_cards(filtered_df: pd.DataFrame):
    """Renders core KPI summary cards."""
    if filtered_df.empty:
        return

    total_births = filtered_df['births'].sum()
    selected_states_cnt = filtered_df['state_of_residence'].nunique()
    
    months_cnt = filtered_df['month'].nunique()
    avg_births_per_month = total_births / months_cnt if months_cnt > 0 else 0

    state_totals = filtered_df.groupby('state_of_residence', observed=True)['births'].sum()
    top_state = state_totals.idxmax() if not state_totals.empty else "N/A"
    top_state_val = state_totals.max() if not state_totals.empty else 0

    month_totals = filtered_df.groupby('month', observed=True)['births'].sum()
    top_month = month_totals.idxmax() if not month_totals.empty else "N/A"
    top_month_val = month_totals.max() if not month_totals.empty else 0

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Births", f"{total_births:,}")
    kpi2.metric("Selected States", f"{selected_states_cnt:,}")
    kpi3.metric("Avg Births / Month", f"{int(round(avg_births_per_month)):,}")
    kpi4.metric("Highest Geography", f"{top_state}", f"{top_state_val:,} births")
    kpi5.metric("Highest Month", f"{top_month}", f"{top_month_val:,} births")

# ==========================================
# VISUALIZATION FUNCTIONS
# ==========================================
def plot_choropleth_map(df: pd.DataFrame):
    """Renders US state choropleth map."""
    state_df = df.groupby(['state_abbr', 'state_of_residence'], as_index=False)['births'].sum()
    fig = px.choropleth(
        state_df,
        locations='state_abbr',
        locationmode="USA-states",
        color='births',
        scope="usa",
        hover_name='state_of_residence',
        hover_data={'births': ':,', 'state_abbr': False},
        color_continuous_scale="Viridis",
        labels={'births': 'Total Births'},
        title="U.S. Birth Distribution by Geography"
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=450)
    return fig

def plot_monthly_trend(df: pd.DataFrame):
    """Renders chronological monthly birth trend line chart."""
    monthly_df = df.groupby('month', observed=True, as_index=False)['births'].sum()
    fig = px.line(
        monthly_df,
        x='month',
        y='births',
        markers=True,
        text=monthly_df['births'].apply(lambda x: f"{x:,}"),
        title="Monthly Birth Trend (Chronological)",
        labels={'month': 'Month', 'births': 'Total Births'}
    )
    fig.update_traces(textposition="top center", line_color="#2b5c8f", line_width=3)
    fig.update_yaxes(rangemode="tozero", tickformat=",d")
    fig.update_layout(height=400)
    return fig

def plot_sex_comparison(df: pd.DataFrame):
    """Renders monthly female vs male grouped bar comparison."""
    sex_df = df.groupby(['month', 'sex_of_infant'], observed=True, as_index=False)['births'].sum()
    fig = px.bar(
        sex_df,
        x='month',
        y='births',
        color='sex_of_infant',
        barmode='group',
        color_discrete_map={'Male': ACCESSIBLE_COLOR_MALE, 'Female': ACCESSIBLE_COLOR_FEMALE},
        title="Monthly Comparison of Male vs. Female Births",
        labels={'month': 'Month', 'births': 'Birth Count', 'sex_of_infant': 'Infant Sex'}
    )
    fig.update_yaxes(rangemode="tozero", tickformat=",d")
    fig.update_layout(height=400)
    return fig

def plot_state_ranking(df: pd.DataFrame):
    """Renders horizontal bar chart of birth counts by state."""
    state_df = df.groupby('state_of_residence', as_index=False)['births'].sum().sort_values('births', ascending=True)
    fig = px.bar(
        state_df,
        x='births',
        y='state_of_residence',
        orientation='h',
        title="Geography Ranking by Total Birth Count",
        labels={'births': 'Total Births', 'state_of_residence': 'State / Geography'}
    )
    fig.update_xaxes(rangemode="tozero", tickformat=",d")
    fig.update_layout(height=max(400, len(state_df) * 18))
    return fig

def plot_top_bottom_comparison(df: pd.DataFrame):
    """Compares top 5 highest and top 5 lowest birth volume states."""
    state_df = df.groupby('state_of_residence', as_index=False)['births'].sum()
    if len(state_df) < 2:
        return None

    sorted_df = state_df.sort_values('births', ascending=False)
    top_5 = sorted_df.head(5).copy()
    top_5['Group'] = 'Top 5 Highest'
    bottom_5 = sorted_df.tail(5).sort_values('births', ascending=True).copy()
    bottom_5['Group'] = 'Top 5 Lowest'
    
    combined = pd.concat([top_5, bottom_5])
    fig = px.bar(
        combined,
        x='births',
        y='state_of_residence',
        color='Group',
        orientation='h',
        title="Comparison: Top 5 Highest vs. Top 5 Lowest Geographies",
        labels={'births': 'Total Births', 'state_of_residence': 'State'},
        color_discrete_map={'Top 5 Highest': '#2ca02c', 'Top 5 Lowest': '#d62728'}
    )
    fig.update_xaxes(rangemode="tozero", tickformat=",d")
    fig.update_layout(height=400)
    return fig

def plot_heatmap(df: pd.DataFrame):
    """Renders state-by-month heatmap matrix."""
    pivot_df = df.pivot_table(
        index='state_of_residence', 
        columns='month', 
        values='births', 
        aggfunc='sum',
        observed=False
    ).fillna(0)

    fig = px.imshow(
        pivot_df,
        labels=dict(x="Month", y="State / Geography", color="Births"),
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        color_continuous_scale="Cividis",
        title="State-by-Month Birth Count Heatmap Matrix"
    )
    fig.update_layout(height=max(450, len(pivot_df) * 16))
    return fig

# ==========================================
# MAIN APPLICATION LOGIC
# ==========================================
def main():
    df = load_data()

    render_header()
    st.markdown("---")

    selected_states, selected_months, selected_sex = render_sidebar(df)
    filtered_df = filter_data(df, selected_states, selected_months, selected_sex)

    if filtered_df.empty:
        st.error("⚠️ No observations match your active filter selections. Please adjust or reset the sidebar filters.")
        return

    render_kpi_cards(filtered_df)
    st.markdown("---")

    tab_overview, tab_geo, tab_month_sex, tab_table, tab_about = st.tabs([
        "📊 Overview",
        "🗺️ Geographic Analysis",
        "📈 Monthly & Sex Analysis",
        "💾 Data Table & Download",
        "ℹ️ About the Data"
    ])

    # TAB 1: OVERVIEW
    with tab_overview:
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.plotly_chart(plot_choropleth_map(filtered_df), use_container_width=True)
        with col2:
            st.plotly_chart(plot_monthly_trend(filtered_df), use_container_width=True)

    # TAB 2: GEOGRAPHIC ANALYSIS
    with tab_geo:
        st.subheader("Geographic Variation & Volume Analysis")
        col_g1, col_g2 = st.columns([1, 1])
        with col_g1:
            fig_top_bottom = plot_top_bottom_comparison(filtered_df)
            if fig_top_bottom:
                st.plotly_chart(fig_top_bottom, use_container_width=True)
            else:
                st.info("Select at least 2 geographies to view top/bottom comparisons.")
        with col_g2:
            st.plotly_chart(plot_heatmap(filtered_df), use_container_width=True)

        st.plotly_chart(plot_state_ranking(filtered_df), use_container_width=True)

    # TAB 3: MONTHLY & SEX ANALYSIS
    with tab_month_sex:
        st.subheader("Demographic & Seasonal Breakdowns")
        col_s1, col_s2 = st.columns([1.2, 0.8])
        with col_s1:
            st.plotly_chart(plot_sex_comparison(filtered_df), use_container_width=True)
        with col_s2:
            st.markdown("#### Summary Insights")
            sex_summary = filtered_df.groupby('sex_of_infant')['births'].sum()
            total = sex_summary.sum()
            
            for sex, val in sex_summary.items():
                pct = (val / total * 100) if total > 0 else 0
                st.metric(f"Total {sex} Births", f"{val:,}", f"{pct:.2f}% of selection")
            
            if 'Male' in sex_summary and 'Female' in sex_summary and sex_summary['Female'] > 0:
                sex_ratio = (sex_summary['Male'] / sex_summary['Female']) * 100
                st.caption(f"**Sex Ratio at Birth**: {sex_ratio:.2f} males per 100 females")

    # TAB 4: DATA TABLE & DOWNLOAD
    with tab_table:
        st.subheader("Filtered Dataset Explorer")
        st.caption(f"Displaying {len(filtered_df):,} matching rows.")
        
        st.dataframe(
            filtered_df[['state_of_residence', 'month', 'year_code', 'sex_of_infant', 'births']],
            use_container_width=True,
            hide_index=True
        )

        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name="CDC_Provisional_Natality_Filtered_2025.csv",
            mime="text/csv"
        )

    # TAB 5: ABOUT THE DATA
    with tab_about:
        st.markdown(
            """
            ### Educational Guidance for Business Analytics
            
            #### 1. Understanding Birth Counts vs. Birth Rates
            * **Birth Count**: The absolute number of live births recorded in a specific state, month, or category.
            * **Birth Rate**: The ratio of births per unit of total population (e.g., per 1,000 population).
            * **Analytic Takeaway**: High birth counts in states like California or Texas are primarily driven by population size rather than higher fertility rates. Avoid concluding that a state has higher birth propensity without standardizing by population.

            #### 2. Provisional Data Status
            * Provisional figures represent early administrative birth certificate records compiled by the CDC National Center for Health Statistics (NCHS).
            * Final counts may differ slightly due to delayed registration and processing validation.

            #### 3. Data Integrity & Best Practices
            * All visualizations start y-axes at zero baseline to prevent visual distortions.
            * Chronological month ordering is enforced across all tables and charts.
            """
        )

if __name__ == "__main__":
    main()