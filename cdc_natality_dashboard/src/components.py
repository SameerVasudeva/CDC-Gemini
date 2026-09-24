import streamlit as st
import pandas as pd

def render_header():
    """Renders dashboard header, CDC attribution, and provisional disclaimer."""
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
    
    # Initialize Session State for filters
    if "selected_states" not in st.session_state:
        st.session_state.selected_states = all_states.copy()
    if "selected_months" not in st.session_state:
        st.session_state.selected_months = all_months.copy()
    if "selected_sex" not in st.session_state:
        st.session_state.selected_sex = "All"

    # Reset Filters Handler
    if st.sidebar.button("🔄 Reset All Filters"):
        st.session_state.selected_states = all_states.copy()
        st.session_state.selected_months = all_months.copy()
        st.session_state.selected_sex = "All"
        st.rerun()

    # Select All State Button
    col_a, col_b = st.sidebar.columns(2)
    if col_a.button("Select All States"):
        st.session_state.selected_states = all_states.copy()
        st.rerun()
    if col_b.button("Clear States"):
        st.session_state.selected_states = []
        st.rerun()

    selected_states = st.sidebar.multiselect(
        "Select Geographies:",
        options=all_states,
        key="selected_states"
    )

    selected_months = st.sidebar.multiselect(
        "Select Months:",
        options=all_months,
        key="selected_months"
    )

    selected_sex = st.sidebar.radio(
        "Infant Sex:",
        options=["All", "Female", "Male"],
        key="selected_sex"
    )

    # Sidebar Filter Summary
    st.sidebar.markdown("---")
    st.sidebar.subheader("Active Filter Summary")
    st.sidebar.caption(f"• **Geographies**: {len(selected_states)} / {len(all_states)} selected")
    st.sidebar.caption(f"• **Months**: {len(selected_months)} / {len(all_months)} selected")
    st.sidebar.caption(f"• **Infant Sex**: {selected_sex}")

    return selected_states, selected_months, selected_sex

def render_kpi_cards(filtered_df: pd.DataFrame):
    """Renders five core KPI summary cards."""
    if filtered_df.empty:
        return

    total_births = filtered_df['births'].sum()
    selected_states_cnt = filtered_df['state_of_residence'].nunique()
    
    # Monthly average calculate
    months_cnt = filtered_df['month'].nunique()
    avg_births_per_month = total_births / months_cnt if months_cnt > 0 else 0

    # Top State
    state_totals = filtered_df.groupby('state_of_residence', observed=True)['births'].sum()
    top_state = state_totals.idxmax() if not state_totals.empty else "N/A"
    top_state_val = state_totals.max() if not state_totals.empty else 0

    # Top Month
    month_totals = filtered_df.groupby('month', observed=True)['births'].sum()
    top_month = month_totals.idxmax() if not month_totals.empty else "N/A"
    top_month_val = month_totals.max() if not month_totals.empty else 0

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    kpi1.metric("Total Births", f"{total_births:,}")
    kpi2.metric("Selected States", f"{selected_states_cnt:,}")
    kpi3.metric("Avg Births / Month", f"{int(round(avg_births_per_month)):,}")
    kpi4.metric("Highest Geography", f"{top_state}", f"{top_state_val:,} births")
    kpi5.metric("Highest Month", f"{top_month}", f"{top_month_val:,} births")
