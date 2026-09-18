"""
Algerian Forest Fires - Model Building & Evaluation
=====================================================
الخطوة 2: بناء نموذج Random Forest للتنبؤ بوقوع الحريق
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, confusion_matrix, classification_report,
                              roc_auc_score, roc_curve)
from sklearn.preprocessing import StandardScaler

DATA_PATH = "../data/cleaned_data.csv"
OUTPUT_DIR = "../outputs"

FEATURES = ['Temperature', 'RH', 'Ws', 'Rain', 'FFMC', 'DMC', 'DC', 'ISI', 'BUI']
TARGET = 'fire_binary'


def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def train_models(df):
    X = df[FEATURES]
    y = df[TARGET]

    # تقسيم البيانات: 80% تدريب، 20% اختبار
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # توحيد المقاييس (مهم للـ Logistic Regression)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}

    # ---- Model 1: Random Forest ----
    rf = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    y_proba_rf = rf.predict_proba(X_test)[:, 1]

    results['Random Forest'] = {
        'model': rf,
        'accuracy': accuracy_score(y_test, y_pred_rf),
        'precision': precision_score(y_test, y_pred_rf),
        'recall': recall_score(y_test, y_pred_rf),
        'f1': f1_score(y_test, y_pred_rf),
        'roc_auc': roc_auc_score(y_test, y_proba_rf),
        'y_pred': y_pred_rf,
        'y_proba': y_proba_rf,
    }

    # ---- Model 2: Logistic Regression (baseline) ----
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    y_pred_lr = lr.predict(X_test_scaled)
    y_proba_lr = lr.predict_proba(X_test_scaled)[:, 1]

    results['Logistic Regression'] = {
        'model': lr,
        'accuracy': accuracy_score(y_test, y_pred_lr),
        'precision': precision_score(y_test, y_pred_lr),
        'recall': recall_score(y_test, y_pred_lr),
        'f1': f1_score(y_test, y_pred_lr),
        'roc_auc': roc_auc_score(y_test, y_proba_lr),
        'y_pred': y_pred_lr,
        'y_proba': y_proba_lr,
    }

    # ---- Cross-validation (للتأكد ماكانش overfitting) ----
    cv_scores = cross_val_score(rf, X, y, cv=5, scoring='accuracy')

    return results, X_test, y_test, cv_scores, rf


def print_results(results, cv_scores):
    print("=" * 60)
    print("مقارنة النماذج")
    print("=" * 60)
    for name, r in results.items():
        print(f"\n{name}:")
        print(f"  Accuracy : {r['accuracy']:.3f}")
        print(f"  Precision: {r['precision']:.3f}")
        print(f"  Recall   : {r['recall']:.3f}")
        print(f"  F1-Score : {r['f1']:.3f}")
        print(f"  ROC-AUC  : {r['roc_auc']:.3f}")

    print(f"\nCross-Validation (5-fold) Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")


def plot_feature_importance(rf, save_path=f"{OUTPUT_DIR}/feature_importance.png"):
    importance = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)

    plt.figure(figsize=(8, 5))
    sns.barplot(x=importance.values, y=importance.index, hue=importance.index,
                palette='YlOrRd_r', legend=False)
    plt.title('Feature Importance for Wildfire Prediction (Random Forest)')
    plt.xlabel('Importance Score')
    plt.ylabel('Feature')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"\n✓ تم حفظ رسم أهمية المتغيرات: {save_path}")
    return importance


def plot_confusion_matrix(y_test, y_pred, save_path=f"{OUTPUT_DIR}/confusion_matrix.png"):
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Not Fire', 'Fire'], yticklabels=['Not Fire', 'Fire'])
    plt.title('Confusion Matrix - Random Forest')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"✓ تم حفظ مصفوفة الالتباس: {save_path}")


def plot_roc_curve(y_test, y_proba, save_path=f"{OUTPUT_DIR}/roc_curve.png"):
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)

    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f'Random Forest (AUC = {auc:.3f})', color='darkorange', linewidth=2)
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"✓ تم حفظ ROC Curve: {save_path}")


if __name__ == "__main__":
    df = load_data()
    results, X_test, y_test, cv_scores, rf = train_models(df)
    print_results(results, cv_scores)

    importance = plot_feature_importance(rf)
    print(f"\nترتيب أهمية المتغيرات:\n{importance}")

    plot_confusion_matrix(y_test, results['Random Forest']['y_pred'])
    plot_roc_curve(y_test, results['Random Forest']['y_proba'])

    print("\n" + "=" * 60)
    print("تفاصيل التقرير الكامل (Random Forest)")
    print("=" * 60)
    print(classification_report(y_test, results['Random Forest']['y_pred'],
                                  target_names=['Not Fire', 'Fire']))
