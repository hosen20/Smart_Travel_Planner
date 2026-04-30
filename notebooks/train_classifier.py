#!/usr/bin/env python
# coding: utf-8

import os
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
import joblib

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / 'data' / 'destinations_dataset.csv'
MODEL_PATH = ROOT / 'models' / 'classifier.joblib'

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

print(f"Loading dataset from {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print('Columns:', df.columns.tolist())
print(df['style'].value_counts())

required_columns = ['destination', 'style']
for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Dataset must include '{column}' column")

# Combine rich destination features into a single text representation.
def build_text_features(df: pd.DataFrame) -> pd.Series:
    df = df.copy()
    df['destination'] = df['destination'].fillna('').astype(str)
    df['country'] = df.get('country', '').fillna('').astype(str)
    df['continent'] = df.get('continent', '').fillna('').astype(str)
    df['climate'] = df.get('climate', '').fillna('').astype(str)
    df['activities'] = df.get('activities', '').fillna('').astype(str)
    df['has_beaches'] = df.get('has_beaches', False).astype(str)
    df['has_mountains'] = df.get('has_mountains', False).astype(str)
    df['is_urban'] = df.get('is_urban', False).astype(str)
    df['is_safe'] = df.get('is_safe', False).astype(str)
    df['is_expensive'] = df.get('is_expensive', False).astype(str)
    df['population'] = df.get('population', '').fillna('').astype(str)
    df['cost_index'] = df.get('cost_index', '').fillna('').astype(str)
    df['safety_index'] = df.get('safety_index', '').fillna('').astype(str)

    return (
        df['destination'] + ' ' +
        df['country'] + ' ' +
        df['continent'] + ' ' +
        df['climate'] + ' ' +
        df['activities'] + ' ' +
        df['has_beaches'] + ' ' +
        df['has_mountains'] + ' ' +
        df['is_urban'] + ' ' +
        df['is_safe'] + ' ' +
        df['is_expensive'] + ' ' +
        df['population'] + ' ' +
        df['cost_index'] + ' ' +
        df['safety_index']
    )

# Prepare data.
df = df.dropna(subset=['destination', 'style']).reset_index(drop=True)
X = build_text_features(df)
y = df['style'].astype(str)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"Training examples: {len(X_train)}")
print(f"Test examples: {len(X_test)}")

classifiers = {
    'RandomForest': RandomForestClassifier(random_state=42, n_estimators=200),
    'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
    'SVM': SVC(random_state=42)
}

results = {}
for name, clf in classifiers.items():
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=2000, ngram_range=(1, 2), stop_words='english')),
        ('clf', clf)
    ])

    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='accuracy')
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    results[name] = {
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'test_accuracy': accuracy_score(y_test, y_pred),
        'classification_report': classification_report(y_test, y_pred, output_dict=True)
    }

    print(f"{name}:")
    print(f"  CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    print(f"  Test Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print()

best_model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=2000, ngram_range=(1, 2), stop_words='english')),
    ('clf', RandomForestClassifier(random_state=42, n_estimators=200))
])

best_model.fit(X_train, y_train)
y_pred = best_model.predict(X_test)
print("Final Model Performance:")
print(classification_report(y_test, y_pred))

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(best_model, MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")

results_df = pd.DataFrame([
    {
        'model': name,
        'cv_accuracy_mean': res['cv_mean'],
        'cv_accuracy_std': res['cv_std'],
        'test_accuracy': res['test_accuracy'],
        'timestamp': pd.Timestamp.now()
    }
    for name, res in results.items()
])
results_df.to_csv(ROOT / 'data' / 'experiment_results.csv', index=False)
print('Results saved to', ROOT / 'data' / 'experiment_results.csv')
