"""
Evaluation utilities: metrics, cross-validation, comparison reports.
"""

from pyspark.sql import DataFrame
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from typing import Dict, List
import json
import os
from datetime import datetime


def evaluate_model(predictions_df, label_col="price", prediction_col="predicted_price"):
    """Compute RMSE, MAE, R2, MSE for a predictions DataFrame."""
    metrics = {}
    for metric_name in ["rmse", "mae", "r2", "mse"]:
        evaluator = RegressionEvaluator(
            labelCol=label_col,
            predictionCol=prediction_col,
            metricName=metric_name
        )
        metrics[metric_name] = evaluator.evaluate(predictions_df)
    return metrics


def cross_validate_model(model_estimator, train_df, num_folds=5, seed=42):
    """Run k-fold CV and return average RMSE."""
    evaluator = RegressionEvaluator(
        labelCol="price",
        predictionCol="predicted_price",
        metricName="rmse"
    )

    param_grid = ParamGridBuilder().build()

    cv = CrossValidator(
        estimator=model_estimator,
        estimatorParamMaps=param_grid,
        evaluator=evaluator,
        numFolds=num_folds,
        seed=seed
    )

    cv_model = cv.fit(train_df)
    avg_metric = cv_model.avgMetrics[0]

    print(f"  {num_folds}-fold CV RMSE: ${avg_metric:,.2f}")

    return {
        "avg_rmse": avg_metric,
        "num_folds": num_folds,
    }


def extract_feature_importance(model, feature_names, model_name):
    """Get feature importances (works with RF/GBT featureImportances and LR coefficients)."""
    importances = []

    if hasattr(model, "featureImportances"):
        raw = model.featureImportances.toArray()
    elif hasattr(model, "coefficients"):
        raw = [abs(c) for c in model.coefficients.toArray()]
    else:
        return importances

    for i, val in enumerate(raw):
        name = feature_names[i] if i < len(feature_names) else f"feature_{i}"
        importances.append({"feature": name, "importance": float(val)})

    importances.sort(key=lambda x: x["importance"], reverse=True)
    return importances


def compare_models(model_results: Dict[str, Dict]) -> Dict:
    """Pick the best model by test R2 and build a comparison summary dict."""
    best_model = None
    best_r2 = -float("inf")

    for name, result in model_results.items():
        test_r2 = result["test_metrics"]["r2"]
        if test_r2 > best_r2:
            best_r2 = test_r2
            best_model = name

    comparison = {
        "compared_at": datetime.now().isoformat(),
        "best_model": best_model,
        "models": {}
    }

    for name, result in model_results.items():
        comparison["models"][name] = {
            "train_metrics": result["train_metrics"],
            "test_metrics": result["test_metrics"],
            "cv_results": result.get("cv_results", {}),
            "feature_importance": result.get("feature_importance", [])[:15],
            "is_best": name == best_model,
        }

    print(f"\nBest model: {best_model} (Test R2: {best_r2:.4f})")
    return comparison


def generate_model_report(comparison, output_path):
    """Generate HTML report comparing all trained models."""
    best_model = comparison["best_model"]
    best_metrics = comparison["models"][best_model]["test_metrics"]

    model_rows = ""
    for name, data in comparison["models"].items():
        test = data["test_metrics"]
        train = data["train_metrics"]
        cv = data.get("cv_results", {})
        badge = ' style="background:#e8f5e9;font-weight:bold;"' if data["is_best"] else ""
        model_rows += f"""
            <tr{badge}>
                <td>{name}{"  (Best)" if data["is_best"] else ""}</td>
                <td>${test['rmse']:,.0f}</td>
                <td>${test['mae']:,.0f}</td>
                <td>{test['r2']:.4f}</td>
                <td>{train['r2']:.4f}</td>
                <td>${cv.get('avg_rmse', 0):,.0f}</td>
            </tr>"""

    importance_rows = ""
    best_importances = comparison["models"][best_model].get("feature_importance", [])
    max_importance = best_importances[0]["importance"] if best_importances else 1
    for item in best_importances[:15]:
        bar_width = (item["importance"] / max_importance * 100) if max_importance > 0 else 0
        importance_rows += f"""
            <tr>
                <td>{item['feature']}</td>
                <td>{item['importance']:.4f}</td>
                <td><div style="background:#4CAF50;height:20px;width:{bar_width:.1f}%;border-radius:3px;"></div></td>
            </tr>"""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Model Comparison Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; flex: 1; text-align: center; }}
        .summary-card h3 {{ margin: 0; color: #4CAF50; font-size: 2em; }}
        .summary-card p {{ margin: 5px 0 0 0; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #4CAF50; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; background: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Model Comparison Report</h1>
        <p><strong>Generated:</strong> {comparison['compared_at']}</p>

        <div class="summary">
            <div class="summary-card">
                <h3>{best_model}</h3>
                <p>Best Model</p>
            </div>
            <div class="summary-card">
                <h3>{best_metrics['r2']:.4f}</h3>
                <p>Test R2 Score</p>
            </div>
            <div class="summary-card">
                <h3>${best_metrics['rmse']:,.0f}</h3>
                <p>Test RMSE</p>
            </div>
            <div class="summary-card">
                <h3>${best_metrics['mae']:,.0f}</h3>
                <p>Test MAE</p>
            </div>
        </div>

        <h2>Model Comparison</h2>
        <table>
            <tr>
                <th>Model</th>
                <th>Test RMSE</th>
                <th>Test MAE</th>
                <th>Test R2</th>
                <th>Train R2</th>
                <th>CV RMSE (5-fold)</th>
            </tr>
            {model_rows}
        </table>

        <h2>Feature Importance ({best_model})</h2>
        <table>
            <tr>
                <th>Feature</th>
                <th>Importance</th>
                <th>Relative</th>
            </tr>
            {importance_rows}
        </table>
    </div>
</body>
</html>
"""

    with open(output_path, 'w') as f:
        f.write(html)
    print(f"Model comparison report saved: {output_path}")


def save_comparison_json(comparison, output_path):
    """Save comparison dict as JSON."""
    with open(output_path, 'w') as f:
        json.dump(comparison, f, indent=2, default=str)
    print(f"Saved: {output_path}")


def save_feature_importance_json(feature_importances, output_path):
    """Save feature importance for all models."""
    with open(output_path, 'w') as f:
        json.dump(feature_importances, f, indent=2, default=str)
    print(f"Saved: {output_path}")
