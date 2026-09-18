"""
Algerian Wildfire Risk Predictor — Interactive Web App
========================================================
Streamlit app that loads the trained Random Forest model and lets
users predict wildfire risk from live meteorological inputs.

Run locally:
    streamlit run app.py

Or deploy for free at: https://share.streamlit.io
"""

import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Page config
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Algerian Wildfire Risk Predictor",
    page_icon="🔥",
    layout="centered",
)

FEATURES = ["Temperature", "RH", "Ws", "Rain", "FFMC", "DMC", "DC", "ISI", "BUI"]

FEATURE_INFO = {
    "Temperature": ("Temperature (°C)", 20.0, 45.0, 32.0, "Noon air temperature"),
    "RH":          ("Relative Humidity (%)", 15.0, 95.0, 62.0, "Relative humidity at noon"),
    "Ws":          ("Wind Speed (km/h)", 0.0, 35.0, 15.0, "Wind speed"),
    "Rain":        ("Rainfall (mm)", 0.0, 20.0, 0.0, "Total rainfall in the last 24h"),
    "FFMC":        ("FFMC", 20.0, 95.0, 80.0, "Fine Fuel Moisture Code — surface litter dryness"),
    "DMC":         ("DMC", 0.0, 70.0, 15.0, "Duff Moisture Code — mid-layer organic soil moisture"),
    "DC":          ("DC", 5.0, 225.0, 50.0, "Drought Code — deep, long-term dryness"),
    "ISI":         ("ISI", 0.0, 20.0, 5.0, "Initial Spread Index — expected fire spread rate"),
    "BUI":         ("BUI", 0.0, 70.0, 17.0, "Buildup Index — total fuel available to combustion"),
}


@st.cache_resource
def load_model():
    return joblib.load("models/rf_model.joblib")


def main():
    st.title("🔥 Algerian Wildfire Risk Predictor")
    st.markdown(
        "Predict daily wildfire occurrence risk from meteorological and "
        "Fire Weather Index (FWI) inputs, using a Random Forest model "
        "trained on the [Algerian Forest Fires Dataset](https://archive.ics.uci.edu/dataset/547/algerian+forest+fires+dataset) "
        "(98% test accuracy — see the [paper](paper/wildfire_paper.pdf) for details)."
    )

    try:
        model = load_model()
    except FileNotFoundError:
        st.error(
            "Model file not found. Run `python src/03_save_model.py` first "
            "to generate `models/rf_model.joblib`."
        )
        st.stop()

    st.subheader("Enter today's conditions")

    col1, col2 = st.columns(2)
    inputs = {}
    for i, feat in enumerate(FEATURES):
        label, lo, hi, default, help_text = FEATURE_INFO[feat]
        col = col1 if i % 2 == 0 else col2
        inputs[feat] = col.slider(label, min_value=lo, max_value=hi, value=default, help=help_text)

    st.divider()

    if st.button("🔮 Predict Fire Risk", type="primary", use_container_width=True):
        X = pd.DataFrame([inputs])[FEATURES]
        proba = model.predict_proba(X)[0][1]
        prediction = model.predict(X)[0]

        if prediction == 1:
            st.error(f"### ⚠️ High Fire Risk — {proba*100:.1f}% probability")
            st.markdown("Conditions resemble historical **fire days** in the dataset.")
        else:
            st.success(f"### ✅ Low Fire Risk — {proba*100:.1f}% probability")
            st.markdown("Conditions resemble historical **non-fire days** in the dataset.")

        st.progress(float(proba))

        with st.expander("Why this prediction? (feature importance)"):
            importance = pd.Series(model.feature_importances_, index=FEATURES).sort_values()
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.barh(importance.index, importance.values, color="#d9534f")
            ax.set_xlabel("Importance Score")
            ax.set_title("Random Forest Feature Importance")
            st.pyplot(fig)
            st.caption(
                "ISI and FFMC dominate the model's decisions, consistent with fire "
                "science — both directly encode fuel flammability and spread rate."
            )

    st.divider()
    st.caption(
        "⚠️ Educational/research demo only — not an operational fire-danger warning system. "
        "Trained on 244 records from a single 2012 fire season in two Algerian regions. "
        "See the paper's Limitations section before drawing strong conclusions."
    )
    st.caption(
        "[GitHub Repository](https://github.com/Machine-Learning-Based-Wildfire/"
        "Machine-Learning-pipeline-predicts-daily-wildfires-in-Algeria) · "
        "Built with scikit-learn + Streamlit"
    )


if __name__ == "__main__":
    main()
