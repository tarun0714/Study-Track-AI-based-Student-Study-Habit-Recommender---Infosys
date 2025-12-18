import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from . import models
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib
import os

# Define paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(APP_DIR)
MODEL_DIR = os.path.join(BACKEND_DIR, "model")
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

MODEL_PATH = os.path.join(MODEL_DIR, "kmeans_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
META_PATH = os.path.join(MODEL_DIR, "cluster_meta.pkl")

def apply_clustering(db: Session):
    """
    Applies K-Means clustering (K=3) to students based on study logs.
    Follows logic from 'clustering.ipynb'.
    """
    # 1. Fetch Data
    logs_query = db.query(models.StudyLog).statement
    df = pd.read_sql(logs_query, db.bind)

    if df.empty:
        return {"message": "No study logs found. Clustering skipped."}

    # 2. Aggregation (Group by student_id)
    # Ensure column names match DB model (lowercase usually in pd.read_sql)
    # Adjust if needed based on actual SQL output, but usually consistent with model attributes
    
    # Check columns first
    valid_cols = ['student_id', 'study_hour', 'distraction_time', 'quiz_score']
    if not all(col in df.columns for col in valid_cols):
        return {"message": f"Missing columns in data. Found: {df.columns}"}

    agg_df = df.groupby('student_id').agg({
        'study_hour': 'mean',
        'distraction_time': 'mean',
        'quiz_score': 'mean'
    }).reset_index()

    if len(agg_df) < 3:
        return {"message": "Not enough students to form 3 clusters."}

    # 3. Feature Engineering
    # Avoid division by zero
    agg_df['Efficiency'] = agg_df['study_hour'] / (agg_df['distraction_time'] + 0.001)
    agg_df['Quiz_per_hour'] = agg_df['quiz_score'] / (agg_df['study_hour'] + 0.001)

    features = ['study_hour', 'distraction_time', 'quiz_score', 'Efficiency', 'Quiz_per_hour']
    
    # 4. Standardization
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(agg_df[features])

    # 5. K-Means Clustering (K=3 as optimized in notebook)
    kmeans = KMeans(n_clusters=3, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    agg_df['Cluster'] = labels

    # Save artifacts for recommender
    joblib.dump(kmeans, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump({"feature_cols": features}, META_PATH)

    # 6. Interpret Clusters
    # We characterize clusters by their centroids' relative performance
    # E.g., High Quiz Score + High Study Hour = High Achiever
    
    # Calculate mean of key metrics per cluster
    cluster_stats = agg_df.groupby('Cluster')[['quiz_score', 'distraction_time']].mean()
    
    # Sort clusters by quiz_score to assign meaningful labels
    # Rank 0 = Lowest Score -> Needs Support / Distracted
    # Rank 1 = Mid Score -> Balanced
    # Rank 2 = High Score -> High Achiever
    
    # Create mapping: Cluster ID -> (Label, Insights)
    sorted_clusters = cluster_stats.sort_values(by='quiz_score')
    
    cluster_mapping = {}
    
    rank_labels = [
        ("Needs Focus", "High distraction or low scores detected. Review basics."),
        ("Balanced", "Consistent performance. Keep improving your focus time."),
        ("High Achiever", "Excellent performance! Keep it up.")
    ]
    
    for rank, (cluster_id, _) in enumerate(sorted_clusters.iterrows()):
        label, insight = rank_labels[rank]
        cluster_mapping[cluster_id] = (label, insight)

    # Save artifacts including mapping
    # We update the meta dump here to include the dynamic mapping
    meta_data = {
        "feature_cols": features,
        "cluster_mapping": cluster_mapping
    }
    joblib.dump(meta_data, META_PATH)

    # 7. Update Database
    for _, row in agg_df.iterrows():
        s_id = row['student_id']
        c_id = row['Cluster']
        label, insight = cluster_mapping.get(c_id, ("Uncategorized", ""))
        
        student = db.query(models.Student).filter(models.Student.student_id == s_id).first()
        if student:
            student.cluster_label = label
            student.cluster_insights = insight
    
    db.commit()
    
    return {
        "message": f"Clustering applied to {len(agg_df)} students.",
        "clusters_found": len(cluster_stats)
    }

if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        print(apply_clustering(db))
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()
