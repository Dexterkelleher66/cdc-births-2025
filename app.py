"""
CDC Provisional Natality 2025 Explorer
Single-File Self-Contained Streamlit Dashboard.
Optimized for zero-configuration deployment on Streamlit Community Cloud.
"""

import os
import pandas as pd
import plotly.express as px
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CDC Provisional Natality 2025 Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONSTANTS & GEOGRAPHIC MAPPING ---
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

STATE_TO_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

COLOR_PRIMARY = "#2563EB"
COLOR_FEMALE = "#EC4899"
COLOR_MALE = "#3B82F6"

# --- DATA LOADER & VALIDATION ---
@st.cache_data(show_spinner="Loading provisional CDC natality data...")
def load_and_validate_data() -> pd.DataFrame:
    """Load, validate, and format provisional natality dataset."""
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "data", "Provisional_Natality_2025_CDC.xlsx"),
        os.path.join("data", "Provisional_Natality_2025_CDC.xlsx"),
        "Provisional_Natality_2025_CDC.xlsx"
    ]
    
    data_path = None
    for p in possible_paths:
        if os.path.exists(p):
            data_path = p
            break
            
    if data_path is None:
        st.error("Data file 'Provisional_Natality_2025_CDC.xlsx' not found. Please ensure it is placed in the 'data/' folder.")
        st.stop()

    df = pd.read_excel(data_path)

    # Benchmark assertions
    assert len(df) == 1224, f"Row count error: expected 1224, got {len(df)}"
    assert df["Births"].sum() == 3604640, f"Births sum error: expected 3604640, got {df['Births'].sum()}"
    assert df["State of Residence"].nunique() == 51, f"Geo count error: expected 51, got {df['State of Residence'].nunique()}"
    assert df.isna().sum().sum() == 0, "Dataset contains missing values."

    # Categorical month ordering & state abbreviation
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)
    df["State Code"] = df["State of Residence"].map(STATE_TO_ABBREV)

    return df

# --- UI COMPONENTS ---
def render_header():
    """Render header banner with CDC attribution, provisional notice, and metric warnings."""
    st.markdown(
        """
        <div style="background-color: #F8FAFC; padding: 1.5rem; border-radius: 0.75rem; border-left: 6px solid #2563EB; margin-bottom: 1.5rem;">
            <h1 style="color: #0F172A; margin: 0; font-size: 2.2rem; font-weight: 700;">
                📊 CDC Provisional Natality 2025 Explorer
            </h1>
            <p style="color: #334155; font-size: 1.05rem; margin-top: 0.5rem; margin-bottom: 1rem; line-height: 1.5;">
                An interactive business analytics dashboard for exploring provisional 2025 U.S. birth trends 
                across 51 geographies, 12 months, and infant sexes. Designed for undergraduate analytics students.
            </p>
            <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center;">
                <span style="background-color: #DBEAFE; color: #1E40AF; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 600; font-size: 0.85rem;">
                    🏛️ Source: CDC National Center for Health Statistics (NCHS)
                </span>
                <span style="background-color: #FEF3C7; color: #92400E; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 600; font-size: 0.85rem;">
                    ⚠️ Notice: Provisional 2025 Data
                </span>
                <span style="background-color: #FEE2E2; color: #991B1B; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 600; font-size: 0.85rem;">
                    📈 Metric: Raw Birth Counts (Not Rates)
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.expander("📌 Analytics Note for Students: Birth Counts vs. Population Rates", expanded=False):
        st.info(
            """
            **Why does the warning say 'Birth Counts, Not Birth Rates'?**
            * **Birth Count**: The raw number of infants born within a specified region and timeframe.
            * **Birth Rate**: The number of births divided by the total resident population (e.g., *births per 1,000 women aged 15–44*).
            
            Because this CDC dataset provides raw count figures without resident population denominator data, 
            calculating population birth rates is mathematically impossible from this file alone.
            """
        )

def render_kpis(df_filtered: pd.DataFrame):
    """Render 5 metric KPI cards."""
    if df_filtered.empty:
        return

    total_births = int(df_filtered["Births"].sum())
    num_geos = df_filtered["State of Residence"].nunique()
    selected_months = df_filtered["Month"].nunique()
    avg_monthly_births = int(total_births / selected_months) if selected_months > 0 else 0

    geo_sums = df_filtered.groupby("State of Residence")["Births"].sum()
    top_geo = geo_sums.idxmax() if not geo_sums.empty else "N/A"
    top_geo_count = int(geo_sums.max()) if not geo_sums.empty else 0

    month_sums = df_filtered.groupby("Month", observed=False)["Births"].sum()
    top_month = month_sums.idxmax() if not month_sums.empty else "N/A"
    top_month_count = int(month_sums.max()) if not month_sums.empty else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Birth Count", f"{total_births:,}", help="Sum of recorded births in active selection.")
    with col2:
        st.metric("Selected Geographies", f"{num_geos} / 51", help="Count of distinct states selected.")
    with col3:
        st.metric("Avg Births / Month", f"{avg_monthly_births:,}", help="Average birth count per selected month.")
    with col4:
        st.metric("Top Geography", top_geo, delta=f"{top_geo_count:,} births", delta_color="normal")
    with col5:
        st.metric("Peak Month", str(top_month), delta=f"{top_month_count:,} births", delta_color="normal")

# --- PLOTLY CHARTS ---
def plot_monthly_trend(df_filtered: pd.DataFrame):
    monthly_data = df_filtered.groupby("Month", observed=False)["Births"].sum().reset_index()
    max_val = monthly_data["Births"].max() if not monthly_data.empty else 100
    fig = px.bar(
        monthly_data, x="Month", y="Births", text_auto=",.0f",
        title="<b>Monthly Birth Distribution (2025 Provisional)</b>",
        labels={"Births": "Total Births", "Month": "Month of Birth"},
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    fig.update_layout(yaxis=dict(range=[0, max_val * 1.18], tickformat=","), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Total Births: %{y:,}<extra></extra>", textposition="outside")
    return fig

def plot_sex_comparison(df_filtered: pd.DataFrame):
    sex_data = df_filtered.groupby("Sex of Infant")["Births"].sum().reset_index()
    max_val = sex_data["Births"].max() if not sex_data.empty else 100
    fig = px.bar(
        sex_data, x="Sex of Infant", y="Births", color="Sex of Infant",
        color_discrete_map={"Female": COLOR_FEMALE, "Male": COLOR_MALE},
        text_auto=",.0f", title="<b>Infant Sex Distribution (Female vs. Male)</b>",
        labels={"Births": "Total Births", "Sex of Infant": "Infant Sex"}
    )
    fig.update_layout(yaxis=dict(range=[0, max_val * 1.18], tickformat=","), showlegend=False, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Total Births: %{y:,}<extra></extra>", textposition="outside")
    return fig

def plot_state_ranking(df_filtered: pd.DataFrame):
    state_data = df_filtered.groupby("State of Residence")["Births"].sum().reset_index().sort_values(by="Births", ascending=True)
    fig = px.bar(
        state_data, x="Births", y="State of Residence", orientation="h",
        title=f"<b>State Birth Rankings ({len(state_data)} Selected)</b>",
        labels={"Births": "Total Births", "State of Residence": "Geography"},
        color="Births", color_continuous_scale="Blues"
    )
    fig.update_layout(xaxis=dict(tickformat=","), yaxis=dict(autorange="reversed"), height=max(400, len(state_data) * 20), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", coloraxis_showscale=False)
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Total Births: %{x:,}<extra></extra>")
    return fig

def plot_choropleth_map(df_filtered: pd.DataFrame):
    state_geo = df_filtered.groupby(["State of Residence", "State Code"])["Births"].sum().reset_index()
    fig = px.choropleth(
        state_geo, locations="State Code", locationmode="USA-states", color="Births", scope="usa",
        color_continuous_scale="Viridis", title="<b>Geographic Birth Distribution across U.S. States & DC</b>",
        hover_name="State of Residence", labels={"Births": "Total Births", "State Code": "State"}
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), geo=dict(lakecolor="rgba(255, 255, 255, 0)"), paper_bgcolor="#FFFFFF")
    fig.update_traces(hovertemplate="<b>%{hovertext} (%{location})</b><br>Total Births: %{z:,}<extra></extra>")
    return fig

def plot_heatmap(df_filtered: pd.DataFrame):
    pivot_df = df_filtered.pivot_table(index="State of Residence", columns="Month", values="Births", aggfunc="sum", observed=False).fillna(0)
    fig = px.imshow(
        pivot_df, labels=dict(x="Month", y="Geography", color="Births"),
        x=pivot_df.columns.tolist(), y=pivot_df.index.tolist(), aspect="auto",
        color_continuous_scale="YlGnBu", title="<b>State-by-Month Birth Count Heatmap</b>"
    )
    fig.update_layout(height=max(500, len(pivot_df) * 18), margin=dict(l=20, r=20, t=50, b=20), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
    fig.update_traces(hovertemplate="Geography: <b>%{y}</b><br>Month: <b>%{x}</b><br>Births: <b>%{z:,}</b><extra></extra>")
    return fig

def plot_top_bottom_comparison(df_filtered: pd.DataFrame):
    state_sums = df_filtered.groupby("State of Residence")["Births"].sum().reset_index().sort_values(by="Births", ascending=False)
    if len(state_sums) < 10:
        st.info("Select at least 10 geographies to view Top 5 vs Bottom 5 comparison.")
        return None
    top_5 = state_sums.head(5).copy(); top_5["Group"] = "Top 5 Geographies"
    bottom_5 = state_sums.tail(5).copy(); bottom_5["Group"] = "Bottom 5 Geographies"
    combined = pd.concat([top_5, bottom_5])
    fig = px.bar(
        combined, x="State of Residence", y="Births", color="Group",
        color_discrete_map={"Top 5 Geographies": "#0284C7", "Bottom 5 Geographies": "#F43F5E"},
        text_auto=",.0f", title="<b>Top 5 vs. Bottom 5 Geographies by Total Birth Count</b>",
        labels={"Births": "Total Births", "State of Residence": "Geography"}
    )
    fig.update_layout(yaxis=dict(tickformat=","), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Total Births: %{y:,}<extra></extra>", textposition="outside")
    return fig

# --- SIDEBAR FILTERS ---
def apply_sidebar_filters(df: pd.DataFrame):
    st.sidebar.header("🔍 Filter Dashboard")
    all_states = sorted(df["State of Residence"].unique().tolist())
    all_months = MONTH_ORDER.copy()

    if "selected_states" not in st.session_state: st.session_state.selected_states = all_states.copy()
    if "selected_months" not in st.session_state: st.session_state.selected_months = all_months.copy()
    if "selected_sex" not in st.session_state: st.session_state.selected_sex = "All"

    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        st.session_state.selected_states = all_states.copy()
        st.session_state.selected_months = all_months.copy()
        st.session_state.selected_sex = "All"
        st.rerun()

    st.sidebar.markdown("---")

    col_s1, col_s2 = st.sidebar.columns([2, 1])
    with col_s1: st.markdown("**State / Geography**")
    with col_s2:
        if st.button("Select All", key="btn_all_states"):
            st.session_state.selected_states = all_states.copy(); st.rerun()

    selected_states = st.sidebar.multiselect("Select Geographies", all_states, default=st.session_state.selected_states, key="ms_states", label_visibility="collapsed")

    col_m1, col_m2 = st.sidebar.columns([2, 1])
    with col_m1: st.markdown("**Month of Birth**")
    with col_m2:
        if st.button("Select All", key="btn_all_months"):
            st.session_state.selected_months = all_months.copy(); st.rerun()

    selected_months = st.sidebar.multiselect("Select Months", all_months, default=st.session_state.selected_months, key="ms_months", label_visibility="collapsed")

    st.sidebar.markdown("**Infant Sex**")
    selected_sex = st.sidebar.radio("Select Sex", ["All", "Female", "Male"], index=["All", "Female", "Male"].index(st.session_state.selected_sex), horizontal=True, key="radio_sex", label_visibility="collapsed")

    filtered_df = df.copy()
    if selected_states: filtered_df = filtered_df[filtered_df["State of Residence"].isin(selected_states)]
    else: filtered_df = filtered_df.iloc[0:0]

    if selected_months and not filtered_df.empty: filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]
    elif not selected_months: filtered_df = filtered_df.iloc[0:0]

    if selected_sex != "All" and not filtered_df.empty: filtered_df = filtered_df[filtered_df["Sex of Infant"] == selected_sex]

    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Active Filter Summary")
    st.sidebar.markdown(f"• **Geographies**: {len(selected_states)} of 51 selected")
    st.sidebar.markdown(f"• **Months**: {len(selected_months)} of 12 selected")
    st.sidebar.markdown(f"• **Sex Filter**: `{selected_sex}`")
    st.sidebar.markdown(f"• **Matching Rows**: `{len(filtered_df):,}` records")

    return filtered_df

# --- MAIN APP ROUTING ---
def main():
    df = load_and_validate_data()
    render_header()
    df_filtered = apply_sidebar_filters(df)
    render_kpis(df_filtered)

    st.markdown("---")

    if df_filtered.empty:
        st.warning("⚠️ **No data available for the current filter combination.** Please adjust your sidebar filters or click **Reset All Filters**.")
        st.stop()

    tab_overview, tab_geo, tab_monthly_sex, tab_data, tab_about = st.tabs([
        "📈 Overview", "🗺️ Geographic Analysis", "🗓️ Monthly & Sex Analysis", "📄 Data Table & Download", "ℹ️ About the Data"
    ])

    with tab_overview:
        col_c1, col_c2 = st.columns([3, 2])
        with col_c1: st.plotly_chart(plot_monthly_trend(df_filtered), use_container_width=True)
        with col_c2: st.plotly_chart(plot_sex_comparison(df_filtered), use_container_width=True)

    with tab_geo:
        st.plotly_chart(plot_choropleth_map(df_filtered), use_container_width=True)
        st.markdown("---")
        col_r, col_tb = st.columns([1, 1])
        with col_r: st.plotly_chart(plot_state_ranking(df_filtered), use_container_width=True)
        with col_tb:
            fig_tb = plot_top_bottom_comparison(df_filtered)
            if fig_tb: st.plotly_chart(fig_tb, use_container_width=True)

    with tab_monthly_sex:
        st.plotly_chart(plot_heatmap(df_filtered), use_container_width=True)
        st.markdown("---")
        monthly_sex_df = df_filtered.groupby(["Month", "Sex of Infant"], observed=False)["Births"].sum().reset_index()
        fig_sex_trend = px.line(
            monthly_sex_df, x="Month", y="Births", color="Sex of Infant", markers=True,
            title="<b>Monthly Birth Trend by Sex (Female vs. Male)</b>",
            labels={"Births": "Total Births", "Month": "Month of Birth"},
            color_discrete_map={"Female": "#EC4899", "Male": "#3B82F6"}
        )
        fig_sex_trend.update_layout(yaxis=dict(tickformat=","), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig_sex_trend, use_container_width=True)

    with tab_data:
        display_df = df_filtered[["State of Residence", "State Code", "Month", "Month Code", "Year Code", "Sex of Infant", "Births"]].copy()
        st.dataframe(display_df, use_container_width=True, column_config={"Births": st.column_config.NumberColumn("Birth Count", format="%d")}, hide_index=True)
        st.download_button("📥 Download Filtered Data as CSV", display_df.to_csv(index=False).encode("utf-8"), "cdc_provisional_natality_2025_filtered.csv", "text/csv", type="primary")

    with tab_about:
        st.markdown(
            """
            ### 📌 Dataset Source & Scope
            * **Data Provider**: CDC National Center for Health Statistics (NCHS).
            * **Release Type**: Provisional Natality Statistics (2025).
            * **Coverage**: 50 U.S. States + District of Columbia ($3,604,640$ total births across $1,224$ observations).

            ### 📖 Data Dictionary
            * **State of Residence**: Mother's U.S. state of residence at birth.
            * **State Code**: 2-letter postal code.
            * **Month / Month Code**: Birth month (`January` to `December` / 1 to 12).
            * **Year Code**: Reporting year (`2025`).
            * **Sex of Infant**: Biological sex assigned at birth (`Female` / `Male`).
            * **Births**: Raw count of live birth events.
            """
        )

if __name__ == "__main__":
    main()
