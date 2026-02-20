#!/usr/bin/env python3
"""
Run the full ML pipeline: financial calcs -> feature engineering ->
model training (LR, RF, GBT) -> evaluation -> predictions.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql.functions import col
from pyspark.ml.regression import (
    LinearRegression, RandomForestRegressor, GBTRegressor
)

from bead.ingest import create_spark_session
from bead.utils import ensure_directory, print_header, print_section, format_number

from pbda.features import transform_features, get_feature_names
from pbda.financial import add_financial_columns
from pbda.model import (
    train_all_models, predict_prices, save_model,
    FEATURES_COL, LABEL_COL, PREDICTION_COL
)
from pbda.evaluate import (
    evaluate_model, cross_validate_model, extract_feature_importance,
    compare_models, generate_model_report, save_comparison_json,
    save_feature_importance_json
)


def main():
    BASE_PATH = "/Users/jai/Downloads/bigdata_project"
    CARS_PARQUET_PATH = os.path.join(BASE_PATH, "data/processed/cars.parquet")
    COE_PARQUET_PATH = os.path.join(BASE_PATH, "data/processed/coe.parquet")
    OUTPUT_PATH = os.path.join(BASE_PATH, "data/pbda_output")

    print_header("ML PIPELINE - FEATURE ENGINEERING & PRICE PREDICTION")

    ensure_directory(OUTPUT_PATH)
    ensure_directory(os.path.join(OUTPUT_PATH, "models"))

    # Step 1: Spark
    print_section("Step 1: Initializing Spark")
    spark = create_spark_session("CarRecommendation_PBDA")

    # Step 2: Load processed parquet data
    print_section("Step 2: Loading Parquet Data")
    car_df = spark.read.parquet(CARS_PARQUET_PATH)
    print(f"Car records: {format_number(car_df.count())}")

    coe_df = spark.read.parquet(COE_PARQUET_PATH)
    print(f"COE records: {format_number(coe_df.count())}")

    # Step 3: Financial columns
    print_section("Step 3: Financial Calculations")
    car_df = add_financial_columns(car_df)
    car_df.select(
        "carmodel", "price", "parf_rebate", "coe_rebate",
        "scrap_value", "monthly_installment"
    ).show(5, truncate=False)

    # Step 4: Features
    print_section("Step 4: Feature Engineering")
    transformed_df, pipeline_model = transform_features(car_df, coe_df)

    # Step 5: 80/20 split
    print_section("Step 5: Train/Test Split")
    train_df, test_df = transformed_df.randomSplit([0.8, 0.2], seed=42)
    print(f"Train: {format_number(train_df.count())} | Test: {format_number(test_df.count())}")

    # Step 6: Train models
    print_section("Step 6: Training ML Models")
    models = train_all_models(train_df)

    # Step 7: Evaluate each model on train + test
    print_section("Step 7: Model Evaluation")
    model_results = {}
    feature_names = get_feature_names()

    for model_name, model in models.items():
        print(f"\n--- {model_name} ---")

        train_preds_df = model.transform(train_df)
        train_metrics = evaluate_model(train_preds_df)
        print(f"  Train - RMSE: ${train_metrics['rmse']:,.2f}  R2: {train_metrics['r2']:.4f}")

        test_preds_df = model.transform(test_df)
        test_metrics = evaluate_model(test_preds_df)
        print(f"  Test  - RMSE: ${test_metrics['rmse']:,.2f}  R2: {test_metrics['r2']:.4f}")

        importance = extract_feature_importance(model, feature_names, model_name)

        model_results[model_name] = {
            "train_metrics": train_metrics,
            "test_metrics": test_metrics,
            "feature_importance": importance,
        }

    # Step 8: Cross-validation (this takes a while)
    print_section("Step 8: 5-Fold Cross-Validation")
    estimators = {
        "LinearRegression": LinearRegression(
            featuresCol=FEATURES_COL, labelCol=LABEL_COL,
            predictionCol=PREDICTION_COL,
            maxIter=100, regParam=0.1, elasticNetParam=0.5
        ),
        "RandomForest": RandomForestRegressor(
            featuresCol=FEATURES_COL, labelCol=LABEL_COL,
            predictionCol=PREDICTION_COL,
            numTrees=100, maxDepth=10, seed=42
        ),
        "GBT": GBTRegressor(
            featuresCol=FEATURES_COL, labelCol=LABEL_COL,
            predictionCol=PREDICTION_COL,
            maxIter=100, maxDepth=8, stepSize=0.1, seed=42
        ),
    }

    for model_name, estimator in estimators.items():
        print(f"\nCross-validating {model_name}...")
        cv_result = cross_validate_model(estimator, transformed_df, num_folds=5)
        model_results[model_name]["cv_results"] = cv_result

    # Step 9: Compare and pick best
    print_section("Step 9: Model Comparison")
    comparison = compare_models(model_results)
    best_model_name = comparison["best_model"]

    # Step 10: Predict on full dataset with best model
    print_section("Step 10: Generating Predictions")
    best_model = models[best_model_name]
    predictions_df = predict_prices(best_model, transformed_df)

    anomaly_counts = predictions_df.groupBy("anomaly_flag").count().collect()
    for row in anomaly_counts:
        print(f"  {row['anomaly_flag']}: {format_number(row['count'])} cars")

    # Step 11: Save everything
    print_section("Step 11: Saving Outputs")

    for model_name, model in models.items():
        save_model(model, OUTPUT_PATH, f"{model_name.lower()}_model")

    pipeline_model.write().overwrite().save(
        os.path.join(OUTPUT_PATH, "models", "feature_pipeline")
    )
    print("  Feature pipeline saved")

    # drop spark vector columns before saving to parquet
    output_cols = [
        "carmodel", "price", "predicted_price", "price_residual",
        "price_residual_pct", "anomaly_flag",
        "transmission", "fuel_type", "type_of_vehicle",
        "engine_cap", "power", "curb_weight", "mileage",
        "coe", "omv", "arf", "road_tax", "owners",
        "car_age_years", "coe_months_left",
        "parf_rebate", "coe_rebate", "scrap_value",
        "loan_amount", "monthly_installment", "downpayment",
        "monthly_depreciation", "mileage_per_year", "power_to_weight",
        "coe_premium_at_reg", "url", "dealer", "reg_date",
    ]
    existing_cols = [c for c in output_cols if c in predictions_df.columns]

    predictions_df.select(existing_cols).write.mode("overwrite").parquet(
        os.path.join(OUTPUT_PATH, "predictions.parquet")
    )
    print("  Predictions saved")

    generate_model_report(
        comparison,
        os.path.join(OUTPUT_PATH, "model_comparison_report.html")
    )
    save_comparison_json(
        comparison,
        os.path.join(OUTPUT_PATH, "model_comparison.json")
    )

    all_importances = {
        name: result.get("feature_importance", [])
        for name, result in model_results.items()
    }
    save_feature_importance_json(
        all_importances,
        os.path.join(OUTPUT_PATH, "feature_importance.json")
    )

    best_test = comparison["models"][best_model_name]["test_metrics"]
    print_header("ML PIPELINE COMPLETE")
    print(f"""
Best Model: {best_model_name}
  Test R2:   {best_test['r2']:.4f}
  Test RMSE: ${best_test['rmse']:,.2f}
  Test MAE:  ${best_test['mae']:,.2f}
  Records:   {predictions_df.count():,}

Outputs in data/pbda_output/:
  models/          - 3 trained models + feature pipeline
  predictions.parquet
  model_comparison_report.html
  model_comparison.json
  feature_importance.json
""")

    print_section("Sample Predictions")
    predictions_df.select(
        "carmodel", "price", "predicted_price",
        "price_residual_pct", "anomaly_flag"
    ).orderBy(col("price_residual_pct").desc()).show(10, truncate=False)

    spark.stop()

    return comparison


if __name__ == "__main__":
    main()
