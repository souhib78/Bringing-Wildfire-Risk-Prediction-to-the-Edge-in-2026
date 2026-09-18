# 🔌 Embedded Deployment — TinyML Wildfire Sensor Node

This module compresses the wildfire prediction model to run **entirely on a
low-power microcontroller** (ESP32/Arduino-class), with no internet
connection, server, or ML runtime required — pure C, ~1.4 KB of compiled
code.

## Why this matters

The main project (see root README) proves a Random Forest can predict
wildfire risk from weather data with 98% accuracy. This module answers the
natural next question for a real-world deployment: **can the same idea run
on the actual low-power sensor hardware you'd place in a forest?**

## What's here

| File | Purpose |
|---|---|
| `wildfire_model.h` | Auto-generated pure-C implementation of a compressed Random Forest (10 trees, max depth 4) — no external libraries |
| `test_equivalence.c` | Validation harness: re-runs all 49 held-out test rows through the C model and compares against the original Python/scikit-learn predictions |
| `main.ino` | Arduino/ESP32 sketch demonstrating on-device inference with 3 example scenarios and an LED risk indicator |
| `wokwi/` | Config to simulate the circuit online at [wokwi.com](https://wokwi.com) — no physical hardware needed to see it run |

## Model compression trade-off

The full 200-tree model (used for the paper's headline 98% accuracy) is
~295 KB — too large for many microcontrollers' flash/RAM budgets. We
benchmarked smaller configurations:

| Trees | Depth | Test Accuracy | 5-fold CV |
|---|---|---|---|
| 200 | 6 | 98.0% | 98.4% |
| 50  | 5 | 95.9% | 98.0% |
| **10** | **4** | **95.9%** | **96.7%** |
| 8   | 3 | 95.9% | 96.7% |
| 5   | 3 | 98.0% | 96.3% |

We selected **10 trees / depth 4** as a reasonable balance: a 2.1-point
accuracy drop from the full model, for a **~200× reduction in source size**
(295 KB → 5.2 KB) and a compiled code footprint of roughly **1.4 KB**
(measured with `gcc -Os`; actual size on an ARM/Xtensa toolchain will be
similar or smaller due to more compact instruction encoding).

## ✅ Correctness, not just "it compiles"

`test_equivalence.c` doesn't just check the code runs — it re-derives the
**exact same soft-voting algorithm scikit-learn uses internally**
(`RandomForestClassifier` averages each tree's class-probability leaf
estimate, rather than a simple majority vote of hard per-tree labels — an
easy mistake that silently changes predictions near the decision boundary).
After fixing the generator to match this exactly:

```
Tested 49 rows, 0 mismatches.
SUCCESS: C model output matches Python exactly.
```

To reproduce:
```bash
cd embedded
gcc -o test_equivalence test_equivalence.c -lm
./test_equivalence
```

## Try the simulated sensor node (no hardware required)

1. Go to [wokwi.com](https://wokwi.com) → **New Project** → **ESP32**
2. Replace the default `sketch.ino` content with `main.ino`
3. Add a new tab named `wildfire_model.h` and paste its contents
4. Click **▶ Start Simulation** — open the Serial Monitor to see live predictions and watch the LED light up on high-risk scenarios

## ⚠️ What's still needed for a real field deployment

This module proves the **inference** side works on tiny hardware. A
production sensor node would still need:

1. **Real sensors** for Temperature, RH, Wind speed, and Rain (e.g., a
   BME280 + anemometer) — straightforward, off-the-shelf.
2. **On-device computation of the FWI sub-indices** (FFMC, DMC, DC, ISI,
   BUI). These aren't raw sensor readings — they're computed daily from
   weather history using the Canadian FWI system's published recursive
   formulas (Van Wagner, 1987), which carry state from the previous day.
   Porting this calculation to C is a natural next step and is **not yet
   implemented here** — currently the demo uses precomputed example values
   from the dataset.
3. **Power budget validation** on real hardware (solar + battery, deep-sleep
   duty cycling) — the compiled model is tiny, but real-world power
   consumption depends on the sensors and radio (LoRa/WiFi) used to report
   readings, which this module does not yet include.

These three items are the concrete scope for a follow-up systems paper
(see `../paper/`).
