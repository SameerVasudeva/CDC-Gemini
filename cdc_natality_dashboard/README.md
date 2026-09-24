# CDC Provisional Natality 2025 Dashboard

An interactive Streamlit dashboard built for undergraduate business analytics students to explore 2025 CDC provisional birth data across geographies, months, and infant sex.

## Local Setup Instructions

1. Clone or download this repository.
2. Ensure Python 3.9+ is installed.
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Key Features
- **Provisional Data Disclaimers**: Clear distinction between raw birth counts and birth rates.
- **Dynamic Filtering**: Stateful state, month, and sex filters with a single-click reset.
- **Analytics Visualizations**: Interactive map, state rankings, heatmaps, and sex ratio analytics built with Plotly.
- **Data Export**: Searchable data table with instant CSV export.
