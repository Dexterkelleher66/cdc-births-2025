"""
CDC Provisional Natality 2025 Explorer
Main Streamlit Application Entry Point.
"""

import sys
import os

# Ensure project root is at the beginning of sys.path for Streamlit Cloud deployment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import streamlit as st
from utils.data_loader import load_and_validate_data, MONTH_ORDER

from utils.components import (
    render_header,
    render_kpis,
    plot_monthly_trend,
    plot_sex_comparison,
    plot_state_ranking,
    plot_choropleth_map,
    plot_heatmap,
    plot_top_bottom_comparison
)

# Page configuration
st.set_page_config(
    page_title="CDC Provisional Natality 2025 Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_sidebar_filters(df: pd.DataFrame):
    """
    Render interactive sidebar filter controls and return filtered DataFrame.
    Includes Select All toggles, Reset Filters button, and dynamic filter summary.
    """
    st.sidebar.header("🔍 Filter Dashboard")
    st.sidebar.markdown("Customize your view by geography, month, or infant sex.")

    all_states = sorted(df["State of Residence"].unique().tolist())
    all_months = MONTH_ORDER.copy()
    sex_options = ["All", "Female", "Male"]

    # Session State Initialization for filters
    if "selected_states" not in st.session_state:
        st.session_state.selected_states = all_states.copy()
    if "selected_months" not in st.session_state:
        st.session_state.selected_months = all_months.copy()
    if "selected_sex" not in st.session_state:
        st.session_state.selected_sex = "All"

    # Reset Filters Button
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        st.session_state.selected_states = all_states.copy()
        st.session_state.selected_months = all_months.copy()
        st.session_state.selected_sex = "All"
        st.rerun()

    st.sidebar.markdown("---")

    # State Multiselect with Select All
    col_state_hdr, col_state_btn = st.sidebar.columns([2, 1])
    with col_state_hdr:
        st.markdown("**State / Geography**")
    with col_state_btn:
        if st.button("Select All", key="btn_all_states", help="Select all 51 geographies"):
            st.session_state.selected_states = all_states.copy()
            st.rerun()

    selected_states = st.sidebar.multiselect(
        label="Select Geographies",
        options=all_states,
        default=st.session_state.selected_states,
        key="ms_states",
        label_visibility="collapsed"
    )

    # Month Multiselect with Select All
    col_month_hdr, col_month_btn = st.sidebar.columns([2, 1])
    with col_month_hdr:
        st.markdown("**Month of Birth**")
    with col_month_btn:
        if st.button("Select All", key="btn_all_months", help="Select all 12 months"):
            st.session_state.selected_months = all_months.copy()
            st.rerun()

    selected_months = st.sidebar.multiselect(
        label="Select Months",
        options=all_months,
        default=st.session_state.selected_months,
        key="ms_months",
        label_visibility="collapsed"
    )

    # Infant Sex Radio Selector
    st.sidebar.markdown("**Infant Sex**")
    selected_sex = st.sidebar.radio(
        label="Select Sex",
        options=sex_options,
        index=sex_options.index(st.session_state.selected_sex),
        horizontal=True,
        key="radio_sex",
        label_visibility="collapsed"
    )

    # Apply filters to dataset
    filtered_df = df.copy()

    if selected_states:
        filtered_df = filtered_df[filtered_df["State of Residence"].isin(selected_states)]
    else:
        filtered_df = filtered_df.iloc[0:0]  # Empty DataFrame if no states selected

    if selected_months and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]
    elif not selected_months:
        filtered_df = filtered_df.iloc[0:0]

    if selected_sex != "All" and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df["Sex of Infant"] == selected_sex]

    # Dynamic Filter Summary in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Active Filter Summary")
    st.sidebar.markdown(f"• **Geographies**: {len(selected_states)} of 51 selected")
    st.sidebar.markdown(f"• **Months**: {len(selected_months)} of 12 selected")
    st.sidebar.markdown(f"• **Sex Filter**: `{selected_sex}`")
    st.sidebar.markdown(f"• **Matching Rows**: `{len(filtered_df):,}` records")

    return filtered_df

def main():
    # Load and validate raw CDC dataset
    df = load_and_validate_data()

    # Render Header Component
    render_header()

    # Render Sidebar & Get Filtered Data
    df_filtered = apply_sidebar_filters(df)

    # Render KPI Metric Cards
    render_kpis(df_filtered, total_df_rows=len(df))

    st.markdown("---")

    # Handle Empty Filter State
    if df_filtered.empty:
        st.warning(
            "⚠️ **No data available for the current filter combination.**\n\n"
            "Please select at least one geography and one month from the sidebar filters, or click **Reset All Filters**."
        )
        st.stop()

    # Create 5 Dashboard Tabs
    tab_overview, tab_geo, tab_monthly_sex, tab_data, tab_about = st.tabs([
        "📈 Overview",
        "🗺️ Geographic Analysis",
        "🗓️ Monthly & Sex Analysis",
        "📄 Data Table & Download",
        "ℹ️ About the Data"
    ])

    # --- TAB 1: OVERVIEW ---
    with tab_overview:
        st.subheader("Dashboard Overview & Key Trends")
        col_chart1, col_chart2 = st.columns([3, 2])
        with col_chart1:
            fig_trend = plot_monthly_trend(df_filtered)
            st.plotly_chart(fig_trend, use_container_width=True)
        with col_chart2:
            fig_sex = plot_sex_comparison(df_filtered)
            st.plotly_chart(fig_sex, use_container_width=True)

    # --- TAB 2: GEOGRAPHIC ANALYSIS ---
    with tab_geo:
        st.subheader("Geographic Distribution & State Rankings")
        
        # US Choropleth Map
        fig_map = plot_choropleth_map(df_filtered)
        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("---")
        
        col_rank, col_topbot = st.columns([1, 1])
        with col_rank:
            fig_rank = plot_state_ranking(df_filtered)
            st.plotly_chart(fig_rank, use_container_width=True)
        with col_topbot:
            fig_tb = plot_top_bottom_comparison(df_filtered)
            if fig_tb is not None:
                st.plotly_chart(fig_tb, use_container_width=True)

    # --- TAB 3: MONTHLY & SEX ANALYSIS ---
    with tab_monthly_sex:
        st.subheader("Seasonal Patterns & Sex Breakdown")
        
        fig_hm = plot_heatmap(df_filtered)
        st.plotly_chart(fig_hm, use_container_width=True)

        st.markdown("---")
        
        st.subheader("Monthly Birth Trends by Infant Sex")
        monthly_sex_df = (
            df_filtered.groupby(["Month", "Sex of Infant"], observed=False)["Births"]
            .sum()
            .reset_index()
        )
        import plotly.express as px
        fig_sex_trend = px.line(
            monthly_sex_df,
            x="Month",
            y="Births",
            color="Sex of Infant",
            markers=True,
            title="<b>Monthly Birth Trend by Sex (Female vs. Male)</b>",
            labels={"Births": "Total Births", "Month": "Month of Birth"},
            color_discrete_map={"Female": "#EC4899", "Male": "#3B82F6"}
        )
        fig_sex_trend.update_layout(
            yaxis=dict(tickformat=","),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF"
        )
        fig_sex_trend.update_traces(
            hovertemplate="Month: <b>%{x}</b><br>Sex: <b>%{fullData.name}</b><br>Births: <b>%{y:,}</b><extra></extra>"
        )
        st.plotly_chart(fig_sex_trend, use_container_width=True)

    # --- TAB 4: DATA TABLE & DOWNLOAD ---
    with tab_data:
        st.subheader("Searchable Filtered Data Table")
        st.markdown(
            "Below is the raw provisional dataset corresponding to your active filter selections. "
            "You can sort by any column or download the filtered dataset as a CSV file."
        )

        display_df = df_filtered[
            ["State of Residence", "State Code", "Month", "Month Code", "Year Code", "Sex of Infant", "Births"]
        ].copy()

        # Display Dataframe with custom column formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "Births": st.column_config.NumberColumn("Birth Count", format="%d"),
                "Year Code": st.column_config.NumberColumn("Year", format="%d"),
                "Month Code": st.column_config.NumberColumn("Month #", format="%d")
            },
            hide_index=True
        )

        # CSV Download Button
        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name="cdc_provisional_natality_2025_filtered.csv",
            mime="text/csv",
            type="primary"
        )

    # --- TAB 5: ABOUT THE DATA ---
    with tab_about:
        st.subheader("About the CDC Provisional Natality 2025 Dataset")
        st.markdown(
            """
            ### 📌 Dataset Source & Scope
            * **Data Provider**: Centers for Disease Control and Prevention (CDC) - National Center for Health Statistics (NCHS).
            * **Release Type**: Provisional Natality Statistics (2025).
            * **Coverage**: 50 U.S. States + District of Columbia (51 total reporting geographies).
            * **Total Records**: 1,224 observations representing 3,604,640 total births.

            ---

            ### 📖 Data Dictionary
            | Column Name | Data Type | Description |
            | :--- | :--- | :--- |
            | **State of Residence** | String (`object`) | The U.S. State or Territory of the mother's residence at time of birth. |
            | **State Code** | String (`object`) | 2-letter FIPS postal abbreviation for spatial mapping. |
            | **Month** | Categorical | Month of birth (`January` through `December`). |
            | **Month Code** | Integer (`int64`) | Numeric month indicator (1 for Jan through 12 for Dec). |
            | **Year Code** | Integer (`int64`) | Reporting year (`2025`). |
            | **Sex of Infant** | String (`object`) | Biological sex assigned at birth (`Female` or `Male`). |
            | **Births** | Integer (`int64`) | Total raw count of live birth events. |

            ---

            ### 🛡️ Data Quality & Audit Integrity Rules
            During dashboard initialization, an automated audit script checks the dataset against CDC benchmarks:
            1. **Row Count Assertion**: Ensures exactly $1,224$ rows exist ($51 \text{ states} \times 12 \text{ months} \times 2 \text{ sexes}$).
            2. **Sum Assertion**: Confirms total birth volume equals $3,604,640$.
            3. **Completeness Assertion**: Verifies $0$ missing values and $0$ duplicate rows.
            """
        )

if __name__ == "__main__":
    main()
