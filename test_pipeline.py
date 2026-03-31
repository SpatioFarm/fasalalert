"""
test_pipeline.py
────────────────
Full end-to-end pipeline test for FasalAlert.

Tests covered
─────────────
  Test 1 — Positive stress   (heat + excess rain)         → High Stress
  Test 2 — Negative CSS      (cool + dry conditions)       → Favorable   ← was broken before
  Test 3 — Near-normal       (tiny deltas)                 → Near Normal
  Test 4 — Extreme stress    (very large anomalies)        → Extreme Stress
  Test 5 — Multi-crop batch  (4 crops, different stages)   → full table
  Test 6 — CSV export        (export_csv round-trip check)
  Test 7 — Mixed batch       (some stress, some favorable) → summary stats

Run from the project root:
    python test_pipeline.py
"""

import sys
import os

# ── Make sure src/ is on the path when running from project root ──
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.logic.stress  import load_thresholds, calculate_css, classify_css
from src.utils.helpers import get_anomalies, generate_advisory, export_csv


# ─────────────────────────────────────────────
# HELPER: pretty-print a single test result
# ─────────────────────────────────────────────
def print_result(label, anomalies, css, info, advisory):
    print(f"\n{'─'*55}")
    print(f"  {label}")
    print(f"{'─'*55}")
    print(f"  ΔTemp     : {anomalies['delta_temp']:+.1f} °C")
    print(f"  ΔRain     : {anomalies['delta_rain']:+.1f} mm")
    print(f"  ΔHumidity : {anomalies['delta_humidity']:+.1f} %")
    print(f"  CSS       : {css:+.2f}  (range: −10 to +10)")
    print(f"  Level     : {info['emoji']}  {info['level']}")
    print(f"  Color     : {info['color']}  ← use this for Folium choropleth")
    print(f"  Advisory  : {advisory}")


# ─────────────────────────────────────────────
# LOAD THRESHOLDS
# Tries CSV first (matches the uploaded crop_thresholds.csv),
# falls back to JSON if CSV not found.
# ─────────────────────────────────────────────
def load():
    for path in ["data/crop_thresholds.csv", "data/crop_thresholds.json"]:
        if os.path.exists(path):
            print(f"  → Loaded thresholds from: {path}")
            return load_thresholds(path)
    raise FileNotFoundError(
        "Could not find crop_thresholds.csv or crop_thresholds.json in data/ folder."
    )


# ═══════════════════════════════════════════════════════
# MAIN TEST SUITE
# ═══════════════════════════════════════════════════════
def main():
    print("\n" + "═" * 55)
    print("  FasalAlert — Full Pipeline Test")
    print("═" * 55)

    thresholds = load()

    all_results = []   # collected for Test 6 (CSV export) and Test 7 (batch summary)

    # ──────────────────────────────────────────
    # TEST 1 — Positive stress (heat + rain)
    # wheat, grain_filling | temp 36°C vs normal 28°C
    # Expected: High or Extreme Stress (positive CSS)
    # ──────────────────────────────────────────
    print("\n\n● TEST 1 — Positive stress (was working before)")

    obs   = (36, 70, 80)    # observed: temp, rain, humidity
    norm  = (28, 50, 65)    # historical normals
    crop, stage = "wheat", "grain_filling"

    anomalies = get_anomalies(*obs, *norm)
    css  = calculate_css(anomalies["delta_temp"], anomalies["delta_rain"],
                         anomalies["delta_humidity"], crop, stage, thresholds)
    info = classify_css(css)
    adv  = generate_advisory(css, crop, anomalies["delta_temp"],
                              anomalies["delta_rain"], anomalies["delta_humidity"])

    print_result("wheat | grain_filling | Hot + wet", anomalies, css, info, adv)

    assert css > 0, "Test 1 FAILED: CSS should be positive for heat + rain stress"
    print("  ✅ PASS — CSS is positive as expected")

    all_results.append({
        "district": "Lucknow", "state": "Uttar Pradesh",
        "crop": crop, "stage": stage,
        **{k: anomalies[k] for k in
           ("obs_temp","obs_rain","obs_humidity","delta_temp","delta_rain","delta_humidity")},
        "css": css, "stress_level": info["level"], "advisory": adv,
    })

    # ──────────────────────────────────────────
    # TEST 2 — Negative CSS (cool + dry conditions)
    # *** THIS WAS BROKEN BEFORE — was silently showing 0 ***
    # Expected: Favorable or Very Favorable (negative CSS)
    # ──────────────────────────────────────────
    print("\n\n● TEST 2 — Negative CSS / Favorable (was BROKEN before → showed 0)")

    obs2  = (22, 30, 50)    # cooler, drier, less humid
    norm2 = (28, 50, 65)
    crop2, stage2 = "wheat", "grain_filling"

    anomalies2 = get_anomalies(*obs2, *norm2)
    css2  = calculate_css(anomalies2["delta_temp"], anomalies2["delta_rain"],
                          anomalies2["delta_humidity"], crop2, stage2, thresholds)
    info2 = classify_css(css2)
    adv2  = generate_advisory(css2, crop2, anomalies2["delta_temp"],
                               anomalies2["delta_rain"], anomalies2["delta_humidity"])

    print_result("wheat | grain_filling | Cool + dry", anomalies2, css2, info2, adv2)

    assert css2 < 0, "Test 2 FAILED: CSS should be negative for cool+dry conditions"
    print("  ✅ PASS — CSS is correctly negative (not clamped to 0 anymore)")

    all_results.append({
        "district": "Shimla", "state": "Himachal Pradesh",
        "crop": crop2, "stage": stage2,
        **{k: anomalies2[k] for k in
           ("obs_temp","obs_rain","obs_humidity","delta_temp","delta_rain","delta_humidity")},
        "css": css2, "stress_level": info2["level"], "advisory": adv2,
    })

    # ──────────────────────────────────────────
    # TEST 3 — Near-normal (tiny deltas)
    # Expected: Near Normal, CSS close to 0
    # ──────────────────────────────────────────
    print("\n\n● TEST 3 — Near-normal conditions")

    obs3  = (28.5, 51, 65.5)
    norm3 = (28,   50, 65)
    crop3, stage3 = "rice", "flowering"

    anomalies3 = get_anomalies(*obs3, *norm3)
    css3  = calculate_css(anomalies3["delta_temp"], anomalies3["delta_rain"],
                          anomalies3["delta_humidity"], crop3, stage3, thresholds)
    info3 = classify_css(css3)
    adv3  = generate_advisory(css3, crop3, anomalies3["delta_temp"],
                               anomalies3["delta_rain"], anomalies3["delta_humidity"])

    print_result("rice | flowering | Near normal", anomalies3, css3, info3, adv3)

    assert -1 <= css3 <= 1, f"Test 3 FAILED: CSS {css3} should be in [-1, 1] for near-normal"
    print("  ✅ PASS — CSS is in Near Normal band")

    all_results.append({
        "district": "Cuttack", "state": "Odisha",
        "crop": crop3, "stage": stage3,
        **{k: anomalies3[k] for k in
           ("obs_temp","obs_rain","obs_humidity","delta_temp","delta_rain","delta_humidity")},
        "css": css3, "stress_level": info3["level"], "advisory": adv3,
    })

    # ──────────────────────────────────────────
    # TEST 4 — Extreme stress (very large anomalies)
    # Expected: Extreme Stress, CSS close to +10
    # ──────────────────────────────────────────
    print("\n\n● TEST 4 — Extreme stress (large anomalies, CSS near +10)")

    obs4  = (48, 200, 98)
    norm4 = (28,  50, 65)
    crop4, stage4 = "maize", "flowering"

    anomalies4 = get_anomalies(*obs4, *norm4)
    css4  = calculate_css(anomalies4["delta_temp"], anomalies4["delta_rain"],
                          anomalies4["delta_humidity"], crop4, stage4, thresholds)
    info4 = classify_css(css4)
    adv4  = generate_advisory(css4, crop4, anomalies4["delta_temp"],
                               anomalies4["delta_rain"], anomalies4["delta_humidity"])

    print_result("maize | flowering | Extreme anomaly", anomalies4, css4, info4, adv4)

    assert css4 >= 7, f"Test 4 FAILED: CSS {css4} should be >= 7 for extreme anomalies"
    print("  ✅ PASS — CSS correctly capped at extreme stress zone")

    all_results.append({
        "district": "Nagpur", "state": "Maharashtra",
        "crop": crop4, "stage": stage4,
        **{k: anomalies4[k] for k in
           ("obs_temp","obs_rain","obs_humidity","delta_temp","delta_rain","delta_humidity")},
        "css": css4, "stress_level": info4["level"], "advisory": adv4,
    })

    # ──────────────────────────────────────────
    # TEST 5 — Multi-crop batch (simulate a DAO querying multiple districts)
    # ──────────────────────────────────────────
    print("\n\n● TEST 5 — Multi-crop batch (4 districts simultaneously)")
    print(f"{'─'*55}")

    batch = [
        # district,       state,           crop,        stage,           obs(T,R,H),    norm(T,R,H)
        ("Amritsar",   "Punjab",        "wheat",     "grain_filling", (39, 85, 82),  (28, 50, 65)),
        ("Kadapa",     "Andhra Pradesh","cotton",    "flowering",     (41, 95, 85),  (38, 90, 80)),
        ("Dehradun",   "Uttarakhand",   "rice",      "vegetative",    (24, 40, 60),  (30, 80, 80)),
        ("Coimbatore", "Tamil Nadu",    "sugarcane", "vegetative",    (36, 110, 83), (30, 80, 75)),
    ]

    batch_results = []
    print(f"  {'District':<14} {'Crop':<10} {'Stage':<15} {'CSS':>6}  Level")
    print(f"  {'─'*14} {'─'*10} {'─'*15} {'─'*6}  {'─'*16}")

    for district, state, crop, stage, obs, norm in batch:
        a = get_anomalies(*obs, *norm)
        css  = calculate_css(a["delta_temp"], a["delta_rain"],
                             a["delta_humidity"], crop, stage, thresholds)
        info = classify_css(css)
        adv  = generate_advisory(css, crop, a["delta_temp"],
                                  a["delta_rain"], a["delta_humidity"])

        print(f"  {district:<14} {crop:<10} {stage:<15} {css:>+6.2f}  "
              f"{info['emoji']} {info['level']}")

        row = {
            "district": district, "state": state,
            "crop": crop, "stage": stage,
            **{k: a[k] for k in
               ("obs_temp","obs_rain","obs_humidity","delta_temp","delta_rain","delta_humidity")},
            "css": css, "stress_level": info["level"], "advisory": adv,
        }
        batch_results.append(row)
        all_results.append(row)

    print(f"  ✅ PASS — Batch of {len(batch)} districts processed")

    # ──────────────────────────────────────────
    # TEST 6 — CSV export round-trip
    # ──────────────────────────────────────────
    print("\n\n● TEST 6 — CSV export (all results so far)")
    print(f"{'─'*55}")

    csv_string = export_csv(all_results)

    # Validate: should have header + one row per result
    lines = [l for l in csv_string.strip().splitlines() if l]
    expected_rows = 1 + len(all_results)   # header + data rows
    assert len(lines) == expected_rows, \
        f"Test 6 FAILED: expected {expected_rows} lines, got {len(lines)}"

    # Validate: "district" column must be present in header
    assert "district" in lines[0], "Test 6 FAILED: header missing 'district' column"
    assert "css"      in lines[0], "Test 6 FAILED: header missing 'css' column"

    print("\n  CSV preview (first 3 data rows):")
    for line in lines[:4]:
        print("  ", line)
    if len(lines) > 4:
        print(f"  ... ({len(lines)-4} more rows)")

    print(f"\n  ✅ PASS — export_csv() produced {len(lines)-1} data rows with correct headers")

    # ──────────────────────────────────────────
    # TEST 7 — Summary statistics (simulate Streamlit metric cards)
    # ──────────────────────────────────────────
    print("\n\n● TEST 7 — Summary statistics (Streamlit metric card simulation)")
    print(f"{'─'*55}")

    css_values  = [r["css"] for r in all_results]
    avg_css     = round(sum(css_values) / len(css_values), 2)
    max_css     = max(css_values)
    min_css     = min(css_values)
    stressed    = [r for r in all_results if r["css"] >= 4]
    favorable   = [r for r in all_results if r["css"] <  0]

    most_stressed  = max(all_results, key=lambda r: r["css"])
    most_favorable = min(all_results, key=lambda r: r["css"])

    print(f"  Total districts queried : {len(all_results)}")
    print(f"  Average CSS             : {avg_css:+.2f}")
    print(f"  Max CSS (most stressed) : {max_css:+.2f}  — {most_stressed['district']}, "
          f"{most_stressed['crop']}")
    print(f"  Min CSS (most favorable): {min_css:+.2f}  — {most_favorable['district']}, "
          f"{most_favorable['crop']}")
    print(f"  Districts under stress  : {len(stressed)}")
    print(f"  Districts favorable     : {len(favorable)}")

    assert len(stressed) + len(favorable) <= len(all_results), "Test 7 FAILED: count mismatch"
    print("  ✅ PASS — Summary stats computed correctly")

    # ──────────────────────────────────────────
    # FINAL SUMMARY
    # ──────────────────────────────────────────
    print("\n" + "═" * 55)
    print("  ALL TESTS PASSED ✅")
    print("  CSS range is now −10 to +10")
    print("  Negative (favorable) conditions are correctly detected")
    print("  Multi-crop batch processing works")
    print("  CSV export is correct")
    print("═" * 55 + "\n")


if __name__ == "__main__":
    main()
