# FasalAlert — Live Demo Script
**Presenter:** Sathvik (Member 2 — GUI)
**Target Duration:** 4–5 minutes
**Setup:** App running at localhost:8501, browser open, API key active

---

## INTRO (30 seconds)
Say:
"This is FasalAlert — a real-time crop stress advisory dashboard built
for district agricultural officers. I'll now do a live walkthrough using
5 districts across two states, with Wheat at the Grain-filling stage —
one of the most heat-sensitive phases for wheat."

---

## STEP 1 — Sidebar Setup (45 seconds)
Action: In the sidebar, select the following:
- State → Punjab
- Districts → Select: Ludhiana, Amritsar, Karnal, Hisar, Jaipur
- Crop → Wheat
- Growth Stage → Grain-filling

Say:
"I've selected 5 districts across Punjab, Haryana and Rajasthan.
The crop is Wheat and the growth stage is Grain-filling — this is
when wheat is most vulnerable to heat stress. The sidebar lets you
select up to 20 districts at once for state-level monitoring."

---

## STEP 2 — Fetch & Analyse (30 seconds)
Action: Click the "Fetch & Analyse" button.

Say:
"When I click Fetch & Analyse, the app calls the OpenWeatherMap API
for each district's coordinates, computes anomalies against IMD
historical normals, and scores each district using our CSS formula.
All of this happens in under 3 seconds."

---

## STEP 3 — Summary Metric Cards (30 seconds)
Action: Point to the 4 metric cards at the top.

Say:
"At the top we have four summary cards — the average Crop Stress Score
across all selected districts, the hottest district, the wettest, and
the most stressed. This gives an instant overview without needing to
read the full table."

---

## STEP 4 — District Detail Table (45 seconds)
Action: Scroll down to the dataframe table. Point to columns.

Say:
"The district detail table shows every queried district with live
temperature, rainfall, humidity, anomaly values, CSS score and the
specific advisory text. Officers can see at a glance which districts
need attention."

Action: Click the "Download Results as CSV" button.

Say:
"And with one click, the full results can be exported as a CSV file
for offline field use or for sharing with block-level officers."

---

## STEP 5 — Advisory Panels (45 seconds)
Action: Scroll down to the red advisory panels.

Say:
"For any district with a CSS score above 6 — meaning HIGH stress —
the app automatically generates a prominent red advisory panel.
Here you can see Ludhiana with CSS 8.5 is flagged for critical heat
stress, with a specific action: irrigate within 48 hours. Hisar is
also flagged for drought stress."

Say:
"These advisories are crop and stage specific — a CSS of 8.5 during
Grain-filling triggers a different action than the same score during
Sowing. The thresholds are all defined in our crop_thresholds.json
config file."

---

## CLOSING (30 seconds)
Say:
"To summarise — FasalAlert gives district agricultural officers a
single spatial tool to monitor live crop stress across multiple
districts, get instant advisories, and export results — all in
under 3 seconds per query. Thank you."

---

## Quick Troubleshooting (just in case)
| Problem | Fix |
|---|---|
| App won't start | Run: streamlit run src\gui\app.py |
| Browser doesn't open | Go to http://localhost:8501 manually |
| No data after clicking Fetch | Check internet connection |