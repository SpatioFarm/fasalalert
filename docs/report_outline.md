---

## Section 4: GUI Architecture

The FasalAlert dashboard is built entirely using Streamlit, a Python-based 
web framework that enables rapid construction of interactive data applications 
without requiring any frontend expertise. The GUI is structured into two 
primary zones: the input sidebar and the main output area.

### 4.1 Input Sidebar

The sidebar serves as the control panel for the entire application. It 
contains four input widgets arranged in a logical top-to-bottom flow:

- **State Selector (`st.selectbox`):** Allows the user to select an Indian 
  state, which filters the available district list contextually.
- **District Multi-Selector (`st.multiselect`):** Enables bulk selection of 
  up to 20 districts simultaneously, supporting state-wide monitoring by 
  agricultural officers.
- **Crop Selector (`st.selectbox`):** Lets the user specify the active crop 
  from six supported options — Wheat, Rice, Maize, Cotton, Soybean, and 
  Sugarcane — ensuring crop-specific stress thresholds are applied.
- **Growth Stage Selector (`st.radio`):** Allows selection of the current 
  phenological stage (Sowing, Vegetative, Flowering, Grain-filling, Harvest), 
  which determines the CSS weight configuration loaded from 
  `crop_thresholds.json`.
- **Fetch & Analyse Button:** Triggers the full data pipeline — API calls, 
  anomaly computation, CSS scoring, and output rendering — in a single click.

### 4.2 Summary Metric Cards

Upon clicking Fetch & Analyse, four `st.metric` cards are rendered at the 
top of the main area, providing an at-a-glance overview of the selected 
districts. These cards display the average Crop Stress Score (CSS), the 
hottest district by temperature, the wettest district by rainfall, and the 
most stressed district by CSS value.

### 4.3 District Detail Table

A full `st.dataframe` table displays all queried districts with columns 
including District, State, Crop, Growth Stage, Temperature, ΔTemp, Rainfall, 
ΔRainfall, Humidity, CSS score, and Advisory text. A `st.download_button` 
below the table allows users to export the results as a UTF-8 encoded CSV 
file for offline field use.

### 4.4 Advisory Panels

For any district with a CSS value of 6 or above (High stress threshold), 
a prominent `st.error()` panel is automatically rendered. Each panel 
displays the district name, state, crop, CSS score, and a specific 
recommended farmer action such as "Irrigate within 48 hours" or 
"Apply fungicide — high humidity risk." This ensures critical alerts 
are immediately visible without requiring the user to scan the full table.