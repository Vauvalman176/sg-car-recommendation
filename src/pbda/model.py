"""
ML model training - LR, RandomForest, GBT using PySpark MLlib.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, lit
from pyspark.ml.regression import (
    LinearRegression,
    RandomForestRegressor,
    GBTRegressor
)
from typing import Dict, Tuple
import os


LABEL_COL = "price"
FEATURES_COL = "features"
PREDICTION_COL = "predicted_price"

# +/- 15% from predicted = anomaly threshold
OVERPRICED_THRESHOLD = 15.0
UNDERPRICED_THRESHOLD = -15.0


def train_linear_regression(train_df, max_iter=100, reg_param=0.1, elastic_net_param=0.5):
    """Train LR with ElasticNet regularization (baseline model)."""
    print("Training Linear Regression model...")
    lr = LinearRegression(
        featuresCol=FEATURES_COL,
        labelCol=LABEL_COL,
        predictionCol=PREDICTION_COL,
        maxIter=max_iter,
        regParam=reg_param,
        elasticNetParam=elastic_net_param
    )
    lr_model = lr.fit(train_df)
    print(f"  Coefficients: {lr_model.coefficients.size} features")
    print(f"  Intercept: {lr_model.intercept:,.2f}")
    return lr_model, "LinearRegression"


def train_random_forest(train_df, num_trees=100, max_depth=10, seed=42):
    """Train Random Forest regressor."""
    print("Training Random Forest model...")
    rf = RandomForestRegressor(
        featuresCol=FEATURES_COL,
        labelCol=LABEL_COL,
        predictionCol=PREDICTION_COL,
        numTrees=num_trees,
        maxDepth=max_depth,
        seed=seed
    )
    rf_model = rf.fit(train_df)
    print(f"  Trees: {rf_model.getNumTrees}")
    return rf_model, "RandomForest"


def train_gbt(train_df, max_iter=100, max_depth=8, step_size=0.1, seed=42):
    """Train Gradient Boosted Trees regressor."""
    print("Training GBT model...")
    gbt = GBTRegressor(
        featuresCol=FEATURES_COL,
        labelCol=LABEL_COL,
        predictionCol=PREDICTION_COL,
        maxIter=max_iter,
        maxDepth=max_depth,
        stepSize=step_size,
        seed=seed
    )
    gbt_model = gbt.fit(train_df)
    print(f"  Iterations: {max_iter}")
    return gbt_model, "GBT"


def train_all_models(train_df: DataFrame) -> Dict:
    """Train all 3 models, return dict of name -> fitted model."""
    models = {}

    lr_model, lr_name = train_linear_regression(train_df)
    models[lr_name] = lr_model

    rf_model, rf_name = train_random_forest(train_df)
    models[rf_name] = rf_model

    gbt_model, gbt_name = train_gbt(train_df)
    models[gbt_name] = gbt_model

    print(f"\nAll {len(models)} models trained successfully")
    return models


def predict_prices(model, df: DataFrame) -> DataFrame:
    """
    Run predictions and flag anomalies based on residual percentage.
    Overpriced = listed much higher than predicted, underpriced = good deal.
    """
    predictions_df = model.transform(df)

    predictions_df = predictions_df.withColumn(
        "price_residual",
        col(PREDICTION_COL) - col(LABEL_COL)
    )
    predictions_df = predictions_df.withColumn(
        "price_residual_pct",
        (col("price_residual") / col(LABEL_COL)) * 100
    )

    # predicted >> actual means car is underpriced (good deal for buyer)
    # predicted << actual means car is overpriced
    predictions_df = predictions_df.withColumn(
        "anomaly_flag",
        when(col("price_residual_pct") < lit(UNDERPRICED_THRESHOLD), lit("overpriced"))
        .when(col("price_residual_pct") > lit(OVERPRICED_THRESHOLD), lit("underpriced"))
        .otherwise(lit("fair"))
    )

    return predictions_df


def save_model(model, output_path, model_name):
    """Save fitted model to disk."""
    model_path = os.path.join(output_path, "models", model_name)
    model.write().overwrite().save(model_path)
    print(f"  Model saved: {model_path}")
