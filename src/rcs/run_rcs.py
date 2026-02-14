#!/usr/bin/env python3
"""
Run the recommendation pipeline.
Demo: Honda Vezel owner looking for a replacement car.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bead.ingest import create_spark_session
from bead.utils import ensure_directory, print_header, print_section, format_number

from rcs.recommender import (
    recommend, format_results,
    generate_recommendation_report, save_results_json
)


def main():
    BASE_PATH = "/Users/jai/Downloads/bigdata_project"
    PREDICTIONS_PATH = os.path.join(BASE_PATH, "data/pbda_output/predictions.parquet")
    OUTPUT_PATH = os.path.join(BASE_PATH, "data/rcs_output")

    print_header("CAR RECOMMENDATION ENGINE")
    ensure_directory(OUTPUT_PATH)

    # --- Demo use case: Jane's Honda Vezel ---

    user_car = {
        "carmodel": "Honda Vezel 1.5A",
        "type_of_vehicle": "SUV",
        "engine_cap": 1496,
        "power": 131,
        "curb_weight": 1310,
        "mileage": 80000,
        "price": 85000,
        "car_age_years": 6.0,
        "coe_months_left": 48,
        "arf": 15000,
        "coe": 50000,
        "omv": 22000,
    }

    constraints = {
        "vehicle_type": None,          # any type
        "min_coe_months": 60,          # >5 years remaining
        "max_monthly_budget": 1500,    # $1,500/month max
        "max_price": 250000,
    }

    # Spark
    print_section("Step 1: Initializing Spark")
    spark = create_spark_session("CarRecommendation_RCS")

    # Load predictions from ML pipeline
    print_section("Step 2: Loading Predictions")
    predictions_df = spark.read.parquet(PREDICTIONS_PATH)
    print(f"Cars available: {format_number(predictions_df.count())}")

    # Show user car info
    print_section("Step 3: User's Current Car")
    print(f"  Car:      {user_car['carmodel']}")
    print(f"  Type:     {user_car['type_of_vehicle']}")
    print(f"  Engine:   {user_car['engine_cap']}cc / {user_car['power']}bhp")
    print(f"  Mileage:  {user_car['mileage']:,} km")
    print(f"  Age:      {user_car['car_age_years']} years")
    print(f"  COE Left: {user_car['coe_months_left']} months")

    # Run recommendation
    print_section("Step 4: Running Recommendations")
    results = recommend(predictions_df, user_car, constraints, k=5)

    print_section("Step 5: Results")
    format_results(results)

    # Save
    print_section("Step 6: Saving")
    generate_recommendation_report(results, os.path.join(OUTPUT_PATH, "recommendation_report.html"))
    save_results_json(results, os.path.join(OUTPUT_PATH, "recommendation_results.json"))

    # --- Demo 2: Luxury sedan search ---
    print_header("DEMO 2: LUXURY SEDAN SEARCH")

    constraints_luxury = {
        "vehicle_type": "Luxury Sedan",
        "min_coe_months": 60,
        "max_monthly_budget": 2000,
        "max_price": 300000,
    }

    print_section("Filtering for Luxury Sedans")
    results_luxury = recommend(predictions_df, user_car, constraints_luxury, k=5)

    print_section("Luxury Sedan Results")
    format_results(results_luxury)

    generate_recommendation_report(results_luxury, os.path.join(OUTPUT_PATH, "recommendation_report_luxury.html"))
    save_results_json(results_luxury, os.path.join(OUTPUT_PATH, "recommendation_results_luxury.json"))

    # Done
    print_header("RECOMMENDATION PIPELINE COMPLETE")
    print(f"""
Car: {user_car['carmodel']}
Trade-in: ${results['user_summary']['scrap_value']:,.2f}
  (PARF: ${results['user_summary']['parf_rebate']:,.2f} + COE: ${results['user_summary']['coe_rebate']:,.2f})

Demo 1 (Any Type): {len(results['recommendations'])} recs from {results.get('total_candidates', 0):,} candidates
Demo 2 (Luxury):   {len(results_luxury['recommendations'])} recs from {results_luxury.get('total_candidates', 0):,} candidates

Output files in data/rcs_output/
""")

    spark.stop()
    return results


if __name__ == "__main__":
    main()
