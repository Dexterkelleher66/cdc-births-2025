# CDC Provisional Natality 2025 Streamlit Dashboard

An interactive, educational business analytics dashboard built with Python, Streamlit, pandas, and Plotly to analyze provisional 2025 CDC natality data across U.S. states, months, and infant sexes.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Dashboard
Run the Streamlit app locally:
```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
CDC-Births-2025/
├── app.py                     # Main Streamlit application script
├── requirements.txt           # Package dependencies
├── README.md                  # Project documentation & instructions
├── data/
│   └── Provisional_Natality_2025_CDC.xlsx   # Original CDC dataset (UNTOUCHED)
└── utils/                     # Helper modules
    ├── __init__.py
    ├── data_loader.py         # Cached loader (@st.cache_data) & audit assertions
    ├── geo_mapping.py         # State name to 2-letter postal code mapping dictionary
    └── components.py          # UI components, header badges, KPI metrics, & Plotly charts
```

---

## 📊 Dashboard Features & Tabs

1. **📈 Overview Tab**: High-level KPI cards, chronological monthly trends, and infant sex distribution.
2. **🗺️ Geographic Analysis Tab**: Interactive US State choropleth map, ranked state bar chart, and Top 5 vs. Bottom 5 state comparison.
3. **🗓️ Monthly & Sex Analysis Tab**: State-by-month birth count heatmap and dual-series monthly sex trend lines.
4. **📄 Data Table & Download Tab**: Interactive dataframe search/sort interface and CSV export functionality.
5. **ℹ️ About the Data Tab**: Detailed data dictionary, CDC attribution, and data quality validation summary.

---

## 💡 Key Business Analytics Principles

* **Raw Birth Counts vs. Population Rates**: The figures in this dataset are **counts of birth events**, NOT demographic birth rates. Calculating fertility rates requires population denominators (e.g. *women of childbearing age*), which are not present in this workbook.
* **Provisional Data**: Provisional statistics are subject to revision as additional birth certificate records are finalized by state vital statistics offices.
* **Cached Data Performance**: Uses Streamlit's `@st.cache_data` decorator to avoid re-reading the Excel workbook on every user interaction, delivering lightning-fast rendering.
