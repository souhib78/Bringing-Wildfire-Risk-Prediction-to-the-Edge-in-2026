"""
Algerian Forest Fires - Save Trained Model
============================================
الخطوة 3: تدريب النموذج النهائي على كامل البيانات وحفظه
لاستعماله في الواجهة التفاعلية (Streamlit app).
"""

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

DATA_PATH = "../data/cleaned_data.csv"
MODEL_PATH = "../models/rf_model.joblib"

FEATURES = ['Temperature', 'RH', 'Ws', 'Rain', 'FFMC', 'DMC', 'DC', 'ISI', 'BUI']
TARGET = 'fire_binary'

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]
    y = df[TARGET]

    # ندرب على كامل البيانات (مو train/test split) لأن الهدف دابا
    # هو نموذج إنتاجي للواجهة، مو تقييم علمي (التقييم صار في 02_train_model.py)
    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X, y)

    import os
    os.makedirs("../models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"✓ تم حفظ النموذج في {MODEL_PATH}")
    print(f"  عدد الأشجار: {model.n_estimators}")
    print(f"  المتغيرات: {FEATURES}")
