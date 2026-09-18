"""
Random Forest -> Embedded C Code Generator
=============================================
يحول نموذج RandomForestClassifier من scikit-learn إلى كود C خام
(بلا أي مكتبات خارجية) يقدر يتجمّع لأي ميكروكونترولر (Arduino/ESP32).

كل شجرة تتحول لسلسلة if/else متداخلة، والتصويت النهائي (majority vote)
يصير بجمع عدد الأصوات لكل فئة.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import joblib
import os

DATA_PATH = "../data/cleaned_data.csv"
FEATURES = ['Temperature', 'RH', 'Ws', 'Rain', 'FFMC', 'DMC', 'DC', 'ISI', 'BUI']
TARGET = 'fire_binary'

N_ESTIMATORS = 10
MAX_DEPTH = 4


def tree_to_c(tree, tree_index, feature_names):
    """يحول شجرة قرار وحدة لدالة C ترجع احتمال الفئة 1 (fire)،
    بنفس طريقة scikit-learn بالضبط (نسبة عينات التدريب من فئة 1 في الورقة)."""
    t = tree.tree_
    lines = [f"float tree_{tree_index}(float *x) {{"]

    def recurse(node, depth):
        indent = "    " * (depth + 1)
        if t.feature[node] != -2:  # مو ورقة (leaf)
            feat = feature_names[t.feature[node]]
            thresh = t.threshold[node]
            feat_idx = feature_names.index(feat)
            lines.append(f"{indent}if (x[{feat_idx}] <= {thresh:.4f}f) {{")
            recurse(t.children_left[node], depth + 1)
            lines.append(f"{indent}}} else {{")
            recurse(t.children_right[node], depth + 1)
            lines.append(f"{indent}}}")
        else:
            # ورقة: نرجع نسبة عينات الفئة 1 في هاذ الورقة (مو hard class)
            # هذا بالضبط شنو تعمل sklearn (soft voting عبر predict_proba)
            counts = t.value[node][0]
            proba_class1 = counts[1] / counts.sum()
            lines.append(f"{indent}return {proba_class1:.6f}f;")

    recurse(0, 0)
    lines.append("}")
    return "\n".join(lines)


def forest_to_c(model, feature_names, header_path):
    n_trees = len(model.estimators_)
    n_features = len(feature_names)

    lines = [
        "// ===================================================================",
        "// Algerian Wildfire Risk — Embedded Random Forest Model",
        "// Auto-generated from a scikit-learn RandomForestClassifier.",
        f"// {n_trees} trees, max_depth={MAX_DEPTH}, {n_features} input features.",
        "// Feature order: " + ", ".join(feature_names),
        "// ===================================================================",
        "#ifndef WILDFIRE_MODEL_H",
        "#define WILDFIRE_MODEL_H",
        "",
        f"#define N_FEATURES {n_features}",
        f"#define N_TREES {n_trees}",
        "",
    ]

    for i, est in enumerate(model.estimators_):
        lines.append(tree_to_c(est, i, feature_names))
        lines.append("")

    # دالة التصويت النهائية (soft voting: متوسط احتمالات كل الأشجار،
    # بالضبط كيما تعمل RandomForestClassifier.predict() في sklearn)
    lines.append("// Average probability across all trees (matches sklearn's soft-voting exactly).")
    lines.append("float wildfire_predict_proba(float *x) {")
    lines.append("    float sum = 0.0f;")
    for i in range(n_trees):
        lines.append(f"    sum += tree_{i}(x);")
    lines.append(f"    return sum / N_TREES;")
    lines.append("}")
    lines.append("")
    lines.append("// Returns 1 = fire risk, 0 = no fire risk (threshold at 0.5, matching sklearn).")
    lines.append("int wildfire_predict(float *x) {")
    lines.append("    return (wildfire_predict_proba(x) > 0.5f) ? 1 : 0;")
    lines.append("}")
    lines.append("")
    lines.append("#endif // WILDFIRE_MODEL_H")

    code = "\n".join(lines)
    with open(header_path, "w") as f:
        f.write(code)
    return code


if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # النموذج المصغّر (embedded-friendly)
    small_model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH, random_state=42
    )
    small_model.fit(X_train, y_train)

    y_pred = small_model.predict(X_test)
    print("=" * 55)
    print(f"Embedded model: {N_ESTIMATORS} trees, max_depth={MAX_DEPTH}")
    print("=" * 55)
    print(f"Test Accuracy : {accuracy_score(y_test, y_pred):.3f}")
    print(f"Precision     : {precision_score(y_test, y_pred):.3f}")
    print(f"Recall        : {recall_score(y_test, y_pred):.3f}")
    print(f"F1-Score      : {f1_score(y_test, y_pred):.3f}")

    # حفظ نسخة .joblib للأرشيف
    os.makedirs("../models", exist_ok=True)
    joblib.dump(small_model, "../models/rf_model_embedded.joblib")

    # توليد كود C
    os.makedirs("../embedded", exist_ok=True)
    header_path = "../embedded/wildfire_model.h"
    code = forest_to_c(small_model, FEATURES, header_path)

    size_bytes = len(code.encode("utf-8"))
    print(f"\n✓ Generated C header: {header_path}")
    print(f"  Source size: {size_bytes:,} bytes ({size_bytes/1024:.1f} KB)")
    print(f"  Lines of code: {len(code.splitlines())}")
