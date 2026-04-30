"""ML service for destination classification."""

from __future__ import annotations

import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd

from app.logging_config import get_logger
from app.settings import Settings

log = get_logger(__name__)


class MLService:
    """Service for ML operations."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.model: Pipeline | None = None

    def load_model(self) -> None:
        """Load the trained model, training it if necessary and data is available."""
        dataset_path = self.settings.data_path / "destinations_dataset.csv"
        try:
            self.model = joblib.load(self.settings.model_path)
            log.info("Model loaded", path=str(self.settings.model_path))

            if dataset_path.exists() and self.settings.model_path.exists():
                model_mtime = self.settings.model_path.stat().st_mtime
                dataset_mtime = dataset_path.stat().st_mtime
                if dataset_mtime > model_mtime:
                    log.info("Dataset newer than model, retraining", dataset=str(dataset_path))
                    self.train_model(str(dataset_path))
        except FileNotFoundError:
            if dataset_path.exists():
                log.info("Model not found, training from dataset", dataset=str(dataset_path))
                self.train_model(str(dataset_path))
            else:
                log.warning("Model not found and dataset missing", dataset=str(dataset_path))
                self.model = None

    def classify_destination(self, destination: str) -> str:
        """Classify a destination into travel style."""
        if self.model is None:
            raise ValueError("Model not loaded")
        prediction = self.model.predict([destination])[0]
        return prediction

    def _build_training_text(self, df: pd.DataFrame) -> pd.Series:
        """Combine rich destination features into a single text feature."""
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

    def train_model(self, data_path: str) -> dict:
        """Train the classifier model."""
        df = pd.read_csv(data_path)
        if 'destination' not in df.columns or 'style' not in df.columns:
            raise ValueError("Dataset must contain 'destination' and 'style' columns")

        df = df.dropna(subset=['destination', 'style']).reset_index(drop=True)
        X = self._build_training_text(df)
        y = df['style'].astype(str)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=2000, ngram_range=(1, 2), stop_words='english')),
            ('clf', RandomForestClassifier(random_state=42, n_estimators=200))
        ])

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)

        joblib.dump(pipeline, self.settings.model_path)
        self.model = pipeline

        log.info("Model trained and saved", path=str(self.settings.model_path))
        return report
