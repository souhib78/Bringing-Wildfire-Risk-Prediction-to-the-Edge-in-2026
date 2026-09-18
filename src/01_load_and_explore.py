"""
Algerian Forest Fires - Data Loading & Exploration
====================================================
الخطوة 1: تحميل البيانات وفهمها

هذا السكريبت يقرأ ملف CSV الأصلي (اللي فيه منطقتين مدمجين بشكل خاص)
وينظفه ويحضره لمرحلة بناء النموذج.
"""

import pandas as pd
import numpy as np

DATA_PATH = "../data/Algerian_forest_fires_dataset_UPDATE.csv"

def load_raw_data(path=DATA_PATH):
    """
    ملف البيانات الأصلي فيه خاصية غريبة:
    - أول 122 سطر = منطقة Bejaia
    - سطر فاضي + عنوان جديد
    - 122 سطر آخرين = منطقة Sidi Bel-Abbes
    لازم نتعامل معه بعناية.
    """
    # نقرا الملف كامل أولاً باش نشوف الهيكل بالضبط
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    print(f"عدد الأسطر الكلي: {len(lines)}")
    print("أول 5 أسطر:")
    for line in lines[:5]:
        print(line.strip())
    print("...")
    print("الأسطر حوالي المنتصف (وين تتغير المنطقة):")
    for line in lines[120:126]:
        print(line.strip())

    return lines


def clean_and_combine(path=DATA_PATH):
    """
    ينظف البيانات ويدمج المنطقتين في DataFrame واحد
    مع عمود 'Region' يوضح المصدر.
    """
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # نلقاو وين تبدا كل منطقة (الأسطر اللي فيها "Region Dataset")
    header_line_idx = None
    split_idx = None

    for i, line in enumerate(lines):
        if 'day' in line.lower() and 'month' in line.lower():
            if header_line_idx is None:
                header_line_idx = i
            else:
                split_idx = i  # ثاني عنوان = بداية المنطقة الثانية

    columns = [c.strip() for c in lines[header_line_idx].split(',')]

    # منطقة 1: Bejaia
    region1_lines = lines[header_line_idx + 1: split_idx - 1] if split_idx else lines[header_line_idx + 1:]
    region1_data = [l.strip().split(',') for l in region1_lines if l.strip() and ',' in l]

    df1 = pd.DataFrame(region1_data, columns=columns)
    df1['Region'] = 'Bejaia'

    df2 = pd.DataFrame()
    if split_idx:
        region2_header_idx = split_idx
        region2_lines = lines[region2_header_idx + 1:]
        region2_data = [l.strip().split(',') for l in region2_lines if l.strip() and ',' in l]
        df2 = pd.DataFrame(region2_data, columns=columns)
        df2['Region'] = 'Sidi Bel-Abbes'

    df = pd.concat([df1, df2], ignore_index=True)

    # تنظيف أسماء الأعمدة (فراغات زايدة)
    df.columns = [c.strip() for c in df.columns]

    # تحويل الأعمدة الرقمية
    numeric_cols = ['day', 'month', 'year', 'Temperature', 'RH', 'Ws',
                     'Rain', 'FFMC', 'DMC', 'DC', 'ISI', 'BUI', 'FWI']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # تنظيف عمود Classes (فيه أحياناً فراغات: "fire " vs "not fire")
    if 'Classes' in df.columns:
        df['Classes'] = df['Classes'].str.strip().str.lower()
        df['fire_binary'] = df['Classes'].apply(lambda x: 1 if 'not' not in str(x) else 0)

    df = df.dropna(subset=['Temperature']) if 'Temperature' in df.columns else df

    return df


if __name__ == "__main__":
    print("=" * 50)
    print("استكشاف البيانات الخام")
    print("=" * 50)
    load_raw_data()

    print("\n" + "=" * 50)
    print("البيانات بعد التنظيف")
    print("=" * 50)
    df = clean_and_combine()
    print(df.head())
    print(f"\nشكل البيانات النهائي: {df.shape}")
    print(f"\nتوزيع الفئات:\n{df['Classes'].value_counts()}")

    # حفظ نسخة نظيفة
    df.to_csv("../data/cleaned_data.csv", index=False)
    print("\n✓ تم حفظ البيانات النظيفة في data/cleaned_data.csv")
