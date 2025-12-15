import os
import joblib
import numpy as np

# This file is backend/app/recommender.py
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(APP_DIR)
MODEL_DIR = os.path.join(BACKEND_DIR, "model")

MODEL_PATH = os.path.join(MODEL_DIR, "kmeans_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
META_PATH = os.path.join(MODEL_DIR, "cluster_meta.pkl")

if not (os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH) and os.path.exists(META_PATH)):
    raise RuntimeError(
        "Model artifacts not found. Please run the training notebook to create "
        "kmeans_model.pkl, scaler.pkl and cluster_meta.pkl in backend/model."
    )

_kmeans = joblib.load(MODEL_PATH)
_scaler = joblib.load(SCALER_PATH)
_meta = joblib.load(META_PATH)

FEATURE_COLS = _meta["feature_cols"]  # ["study_hour", "distraction_time", "quiz_score"]


def _cluster_profile(cluster_id: int) -> str:
    profiles = {
        0: "Moderate study time, moderate distractions, average quiz performance.",
        1: "High study time, low distractions, strong quiz performance.",
        2: "Low study time, high distractions, weaker quiz scores.",
        3: "Inconsistent study habits with fluctuating performance.",
        4: "Balanced study patterns with good understanding.",
        5: "Very high effort but inconsistent outcomes.",
    }
    return profiles.get(cluster_id, "General study behavior pattern.")


def generate_recommendations(
    study_hour: float,
    distraction_time: float,
    quiz_score: float,
):
    """
    Uses the trained KMeans model and scaler saved in backend/model.
    Inputs must match your dataset's units and naming.
    """
    x = np.array([[study_hour, distraction_time, quiz_score]])
    x_scaled = _scaler.transform(x)
    cluster_id = int(_kmeans.predict(x_scaled)[0])

    profile_desc = _cluster_profile(cluster_id)

    suggestions = []

    # Study time
    if study_hour < 2:
        suggestions.append("Increase your daily study time gradually by 30–45 minutes.")
    elif study_hour > 5:
        suggestions.append("Use shorter, focused sessions with breaks to avoid burnout.")

    # Distraction time (if minutes, threshold ~30; tweak if hours)
    if distraction_time > 30:
        suggestions.append("Try Pomodoro and silence your phone during study sessions.")
    else:
        suggestions.append("Your distraction time seems under control, keep it up.")

    # Quiz score
    if quiz_score < 60:
        suggestions.append("Revise basics and practice easier questions to build confidence.")
    elif 60 <= quiz_score < 80:
        suggestions.append("Focus on weaker topics and mix medium-difficulty questions.")
    else:
        suggestions.append("Challenge yourself with tougher problems and timed tests.")

    return {
        "cluster_id": cluster_id,
        "cluster_profile": profile_desc,
        "recommendations": suggestions,
    }
