"""
Main recommendation logic.
Ties together: scrap value calc -> filtering -> similarity -> upgrade cost.
"""

from pyspark.sql import DataFrame
import pandas as pd
import json
import os
from datetime import datetime

from .filters import apply_all_filters
from .similarity import (
    SIMILARITY_FEATURES, compute_norm_stats,
    build_user_vector, compute_cosine_similarity, get_top_k
)


# same PARF table as in financial.py (duplicated here to keep recommender standalone)
PARF_REBATE_TABLE = [
    (5, 0.75),
    (6, 0.70),
    (7, 0.65),
    (8, 0.60),
    (9, 0.55),
    (10, 0.50),
]


def calculate_user_scrap_value(user_car):
    """Calculate trade-in value: PARF rebate + COE rebate."""
    arf = float(user_car.get("arf", 0))
    age = float(user_car.get("car_age_years", 0))
    coe = float(user_car.get("coe", 0))
    coe_months = float(user_car.get("coe_months_left", 0))

    parf_rebate = 0.0
    for threshold, pct in PARF_REBATE_TABLE:
        if age < threshold:
            parf_rebate = arf * pct
            break

    coe_rebate = coe * max(coe_months, 0) / 120.0
    scrap_value = parf_rebate + coe_rebate

    return {
        "parf_rebate": round(parf_rebate, 2),
        "coe_rebate": round(coe_rebate, 2),
        "scrap_value": round(scrap_value, 2),
    }


def recommend(predictions_df, user_car, constraints, k=5):
    """
    Full recommendation pipeline:
    1) calc user scrap value  2) filter candidates  3) similarity scoring
    4) top-K selection  5) net upgrade cost
    """
    # user's trade-in value
    scrap_info = calculate_user_scrap_value(user_car)
    print(f"\n  User's scrap value: ${scrap_info['scrap_value']:,.2f}")
    print(f"    PARF rebate: ${scrap_info['parf_rebate']:,.2f}")
    print(f"    COE rebate:  ${scrap_info['coe_rebate']:,.2f}")

    # filter
    filtered_df = apply_all_filters(predictions_df, constraints)

    candidate_count = filtered_df.count()
    if candidate_count == 0:
        print("  No candidates match these constraints!")
        return {
            "user_summary": {"carmodel": user_car.get("carmodel", "Unknown"), **scrap_info},
            "constraints": constraints,
            "recommendations": [],
            "generated_at": datetime.now().isoformat(),
        }

    # similarity
    norm_stats = compute_norm_stats(filtered_df, SIMILARITY_FEATURES)
    user_vector = build_user_vector(user_car, SIMILARITY_FEATURES, norm_stats)
    candidates_pd = compute_cosine_similarity(
        user_vector, filtered_df, SIMILARITY_FEATURES, norm_stats
    )

    top_k = get_top_k(candidates_pd, k=k)

    # net upgrade cost = new car price - trade-in value
    user_scrap = scrap_info["scrap_value"]
    top_k["net_upgrade_cost"] = (top_k["price"] - user_scrap).round(2)

    # build results list
    recommendations = []
    for i, row in top_k.iterrows():
        recommendations.append({
            "rank": i + 1,
            "carmodel": row.get("carmodel", ""),
            "price": float(row.get("price", 0)),
            "predicted_price": float(row.get("predicted_price", 0)),
            "similarity_score": float(row.get("similarity_score", 0)),
            "net_upgrade_cost": float(row.get("net_upgrade_cost", 0)),
            "monthly_installment": float(row.get("monthly_installment", 0)),
            "coe_months_left": float(row.get("coe_months_left", 0)),
            "anomaly_flag": str(row.get("anomaly_flag", "")),
            "type_of_vehicle": str(row.get("type_of_vehicle", "")),
            "engine_cap": float(row.get("engine_cap", 0)),
            "power": float(row.get("power", 0)),
            "mileage": float(row.get("mileage", 0)),
            "transmission": str(row.get("transmission", "")),
            "fuel_type": str(row.get("fuel_type", "")),
            "dealer": str(row.get("dealer", "")),
            "url": str(row.get("url", "")),
        })

    return {
        "user_summary": {
            "carmodel": user_car.get("carmodel", "Unknown"),
            **scrap_info,
            "car_age_years": user_car.get("car_age_years", 0),
            "coe_months_left": user_car.get("coe_months_left", 0),
        },
        "constraints": constraints,
        "total_candidates": candidate_count,
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat(),
    }


def format_results(results):
    """Print recommendations table to console."""
    user = results["user_summary"]
    recs = results["recommendations"]

    print(f"\n  User Car: {user['carmodel']}")
    print(f"  Trade-in Value: ${user['scrap_value']:,.2f}")
    print(f"  (PARF: ${user['parf_rebate']:,.2f} + COE: ${user['coe_rebate']:,.2f})")

    if not recs:
        print("\n  No recommendations found.")
        return

    print(f"\n  {'Rank':<5} {'Car Model':<40} {'Price':>12} {'Similarity':>11} {'Net Cost':>12} {'Monthly':>10} {'COE Left':>10} {'Deal':>12}")
    print(f"  {'-'*5} {'-'*40} {'-'*12} {'-'*11} {'-'*12} {'-'*10} {'-'*10} {'-'*12}")

    for rec in recs:
        model = rec["carmodel"][:39]
        print(
            f"  {rec['rank']:<5} {model:<40} "
            f"${rec['price']:>10,.0f} "
            f"{rec['similarity_score']:>10.4f} "
            f"${rec['net_upgrade_cost']:>10,.0f} "
            f"${rec['monthly_installment']:>8,.0f} "
            f"{rec['coe_months_left']:>8.0f}m "
            f"{rec['anomaly_flag']:>12}"
        )


def generate_recommendation_report(results, output_path):
    """Generate HTML report with trade-in info and recommendation table."""
    user = results["user_summary"]
    recs = results["recommendations"]
    constraints = results.get("constraints", {})

    rec_rows = ""
    for rec in recs:
        deal_color = {"underpriced": "#27ae60", "fair": "#f39c12", "overpriced": "#e74c3c"}.get(
            rec["anomaly_flag"], "#666"
        )
        rec_rows += f"""
            <tr>
                <td><strong>#{rec['rank']}</strong></td>
                <td><strong>{rec['carmodel']}</strong><br>
                    <small>{rec['type_of_vehicle']} | {rec['transmission']} | {rec['fuel_type']}</small></td>
                <td>${rec['price']:,.0f}</td>
                <td>{rec['similarity_score']:.4f}</td>
                <td>${rec['net_upgrade_cost']:,.0f}</td>
                <td>${rec['monthly_installment']:,.0f}</td>
                <td>{rec['coe_months_left']:.0f} months</td>
                <td><span style="color:{deal_color};font-weight:bold;">{rec['anomaly_flag'].upper()}</span></td>
            </tr>"""

    constraint_items = ""
    if constraints.get("vehicle_type"):
        constraint_items += f"<li>Vehicle Type: {constraints['vehicle_type']}</li>"
    if constraints.get("min_coe_months"):
        constraint_items += f"<li>Min COE: {constraints['min_coe_months']} months</li>"
    if constraints.get("max_monthly_budget"):
        constraint_items += f"<li>Max Monthly: ${constraints['max_monthly_budget']:,.0f}</li>"
    if constraints.get("max_price"):
        constraint_items += f"<li>Max Price: ${constraints['max_price']:,.0f}</li>"

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Car Recommendation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; flex-wrap: wrap; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; flex: 1; text-align: center; min-width: 150px; }}
        .summary-card h3 {{ margin: 0; color: #4CAF50; font-size: 1.8em; }}
        .summary-card p {{ margin: 5px 0 0 0; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #4CAF50; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
        .user-info {{ background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .constraints {{ background: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .constraints ul {{ margin: 5px 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Car Recommendation Report</h1>
        <p><strong>Generated:</strong> {results.get('generated_at', '')}</p>

        <div class="user-info">
            <h2 style="margin-top:0;">Your Car: {user['carmodel']}</h2>
            <div class="summary">
                <div class="summary-card">
                    <h3>${user['scrap_value']:,.0f}</h3>
                    <p>Trade-in Value</p>
                </div>
                <div class="summary-card">
                    <h3>${user['parf_rebate']:,.0f}</h3>
                    <p>PARF Rebate</p>
                </div>
                <div class="summary-card">
                    <h3>${user['coe_rebate']:,.0f}</h3>
                    <p>COE Rebate</p>
                </div>
                <div class="summary-card">
                    <h3>{user.get('coe_months_left', 0):.0f}m</h3>
                    <p>COE Remaining</p>
                </div>
            </div>
        </div>

        <div class="constraints">
            <strong>Search Constraints:</strong>
            <ul>{constraint_items if constraint_items else "<li>No specific constraints</li>"}</ul>
            <p>Candidates found: {results.get('total_candidates', 0):,}</p>
        </div>

        <h2>Top {len(recs)} Recommendations</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Car Model</th>
                <th>Price</th>
                <th>Similarity</th>
                <th>Net Upgrade Cost</th>
                <th>Monthly</th>
                <th>COE Left</th>
                <th>Deal</th>
            </tr>
            {rec_rows}
        </table>
    </div>
</body>
</html>
"""

    with open(output_path, 'w') as f:
        f.write(html)
    print(f"Report saved: {output_path}")


def save_results_json(results, output_path):
    """Dump results dict to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"JSON saved: {output_path}")
