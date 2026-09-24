import streamlit as st
import pandas as pd
from src.data_loader import load_data, filter_data
from src.components import render_header, render_sidebar, render_kpi_cards
from src.visualizations import (
    plot_choropleth_map,
    plot_monthly_trend,
    plot_sex_comparison,
    plot_state_ranking,
    plot_top_bottom_comparison,
    plot_heatmap
)

# Set page configuration
st.set_page_config(
    page_title="CDC Provisional Natality Explorer 2025",
    page_icon="📊",
    layout="wide"
)

def main():
    # Load dataset
    df = load_data()

    # Header section
    render_header()
    st.markdown("---")

    # Sidebar controls
    selected_states, selected_months, selected_sex = render_sidebar(df)

    # Filter data
    filtered_df = filter_data(df, selected_states, selected_months, selected_sex)

    # Empty State Handling
    if filtered_df.empty:
        st.error("⚠️ No observations match your active filter selections. Please adjust or reset the sidebar filters.")
        return

    # Render KPI Summary Bar
    render_kpi_cards(filtered_df)
    st.markdown("---")

    # Dashboard Tabs
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
        
        # Display Searchable Dataframe
        st.dataframe(
            filtered_df[['state_of_residence', 'month', 'year_code', 'sex_of_infant', 'births']],
            use_container_width=True,
            hide_index=True
        )

        # Download CSV Button
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
