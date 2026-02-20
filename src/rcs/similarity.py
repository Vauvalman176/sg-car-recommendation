"""
Cosine similarity engine for car recommendations.
Uses min-max normalization then cosine sim to rank candidates.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, min as spark_min, max as spark_max
import numpy as np
import pandas as pd
from typing import Dict, List


# features that define what makes two cars "similar"
SIMILARITY_FEATURES = [
    "engine_cap",
    "power",
    "curb_weight",
    "mileage",
    "car_age_years",
]


def compute_norm_stats(df, feature_cols):
    """Get min/max for each feature column (for normalization)."""
    agg_exprs = []
    for c in feature_cols:
        agg_exprs.append(spark_min(c).alias(f"{c}_min"))
        agg_exprs.append(spark_max(c).alias(f"{c}_max"))

    stats_row = df.agg(*agg_exprs).collect()[0]

    norm_stats = {}
    for c in feature_cols:
        min_val = float(stats_row[f"{c}_min"] or 0)
        max_val = float(stats_row[f"{c}_max"] or 1)
        range_val = max_val - min_val if max_val != min_val else 1.0
        norm_stats[c] = {"min": min_val, "max": max_val, "range": range_val}

    return norm_stats


def build_user_vector(user_car, feature_cols, norm_stats):
    """Normalize the user's car specs into a feature vector."""
    vector = []
    for c in feature_cols:
        raw = float(user_car.get(c, 0))
        stats = norm_stats[c]
        normalized = (raw - stats["min"]) / stats["range"]
        vector.append(normalized)
    return np.array(vector)


def compute_cosine_similarity(user_vector, candidates_df, feature_cols, norm_stats):
    """
    Compute cosine similarity between user vector and all candidate cars.
    Converts to pandas/numpy since post-filter candidates are small enough.
    Returns pandas DataFrame with similarity_score column added.
    """
    candidates_pd = candidates_df.toPandas()

    if candidates_pd.empty:
        candidates_pd["similarity_score"] = []
        return candidates_pd

    # normalize candidate features into a matrix
    candidate_matrix = np.zeros((len(candidates_pd), len(feature_cols)))
    for i, c in enumerate(feature_cols):
        stats = norm_stats[c]
        raw_vals = candidates_pd[c].fillna(stats["min"]).values.astype(float)
        candidate_matrix[:, i] = (raw_vals - stats["min"]) / stats["range"]

    # cosine sim = dot(u, v) / (||u|| * ||v||)
    user_norm = np.linalg.norm(user_vector)
    if user_norm == 0:
        user_norm = 1.0

    candidate_norms = np.linalg.norm(candidate_matrix, axis=1)
    candidate_norms[candidate_norms == 0] = 1.0

    dot_products = candidate_matrix @ user_vector
    similarities = dot_products / (user_norm * candidate_norms)
    similarities = np.clip(similarities, 0.0, 1.0)

    candidates_pd["similarity_score"] = np.round(similarities, 4)
    return candidates_pd


def get_top_k(candidates_pd, k=5):
    """Return top K most similar candidates sorted by score."""
    return candidates_pd.nlargest(k, "similarity_score").reset_index(drop=True)
