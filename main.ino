/*
 * Algerian Wildfire Risk — Embedded Demo (ESP32 / Arduino)
 * ===========================================================
 * Runs the compressed Random Forest model (10 trees, ~5 KB source,
 * ~1.4 KB compiled) directly on the microcontroller. No internet,
 * no server, no external ML library — pure C, verified to match
 * the original scikit-learn model on 49/49 held-out test rows.
 *
 * This demo cycles through 3 example scenarios (taken from real
 * dataset test rows) and lights an LED when high fire risk is
 * predicted. In a real deployment, the 9 input features would come
 * from actual sensors (see README for what's still missing).
 *
 * Try it with zero hardware at: https://wokwi.com
 * (open embedded/wokwi/diagram.json in a new Wokwi project)
 */

#include "wildfire_model.h"

#define LED_PIN 2  // onboard LED on most ESP32 dev boards

// Feature order: Temperature, RH, Ws, Rain, FFMC, DMC, DC, ISI, BUI
struct Scenario {
  const char *label;
  float features[N_FEATURES];
};

Scenario scenarios[] = {
  {"High-risk day (real fire-day record)",
   {37.0, 37.0, 18.0, 0.2, 88.9, 12.9, 14.6, 9.0, 12.5}},
  {"Low-risk day (real non-fire-day record)",
   {26.0, 82.0, 12.0, 3.5, 45.0, 3.0, 10.0, 1.0, 4.0}},
  {"Borderline day (near decision boundary)",
   {35.0, 64.0, 18.0, 0.2, 80.0, 9.7, 40.4, 2.8, 12.1}},
};

const int N_SCENARIOS = sizeof(scenarios) / sizeof(scenarios[0]);

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  delay(1000);
  Serial.println("=================================================");
  Serial.println("Algerian Wildfire Risk Predictor — Embedded Demo");
  Serial.println("=================================================");
  Serial.print("Model size: ");
  Serial.print(N_TREES);
  Serial.print(" trees, ");
  Serial.print(N_FEATURES);
  Serial.println(" features. Running fully on-device.");
  Serial.println();
}

void loop() {
  for (int i = 0; i < N_SCENARIOS; i++) {
    float proba = wildfire_predict_proba(scenarios[i].features);
    int prediction = (proba > 0.5f) ? 1 : 0;

    Serial.print("Scenario: ");
    Serial.println(scenarios[i].label);
    Serial.print("  Fire probability: ");
    Serial.print(proba * 100.0f, 1);
    Serial.println("%");
    Serial.print("  Prediction: ");
    Serial.println(prediction == 1 ? "FIRE RISK" : "SAFE");

    digitalWrite(LED_PIN, prediction == 1 ? HIGH : LOW);
    Serial.println("-------------------------------------------------");
    delay(3000);
  }
}
