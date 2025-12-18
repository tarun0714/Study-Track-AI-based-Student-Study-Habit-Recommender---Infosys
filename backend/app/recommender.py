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
    # Use dynamically saved mapping if available, else fallback
    mapping = _meta.get("cluster_mapping", {})
    if cluster_id in mapping:
        label, insight = mapping[cluster_id]
        return f"{label} - {insight}"
    
    # Fallback/Default profiles (should rarely be hit if clustering is run)
    profiles = {
        0: "Needs Focus - Support needed.",
        1: "Balanced - Consistent performance.",
        2: "High Achiever - Excellent results."
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

    x_input = np.array([[study_hour, distraction_time, quiz_score]])
    
    # Feature engineering to match clustering.py
    # features = ['study_hour', 'distraction_time', 'quiz_score', 'Efficiency', 'Quiz_per_hour']
    efficiency = study_hour / (distraction_time + 0.001)
    quiz_per_hour = quiz_score / (study_hour + 0.001)
    
    x_full = np.array([[study_hour, distraction_time, quiz_score, efficiency, quiz_per_hour]])
    
    x_scaled = _scaler.transform(x_full)
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
