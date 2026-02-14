#!/usr/bin/env python3
"""
Data Ingestion Runner
Executes the complete data ingestion and profiling pipeline.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bead.ingest import create_spark_session, load_car_data, load_coe_data, save_as_parquet
from bead.profiler import profile_dataframe, print_profile_summary, generate_profile_report, save_profile_json
from bead.utils import ensure_directory, print_header, print_section


def main():
    """Run the complete data ingestion pipeline."""

    # Configuration
    BASE_PATH = "/Users/jai/Downloads/bigdata_project"
    CAR_DATA_PATH = os.path.join(BASE_PATH, "webscrap_sgcarmart/data/carlist_20260128_with_loan_info.csv")
    COE_DATA_PATH = os.path.join(BASE_PATH, "data/coe/coe_bidding_results.csv")
    OUTPUT_PATH = os.path.join(BASE_PATH, "data/processed")

    print_header("DATA INGESTION PIPELINE")

    # Ensure output directory exists
    ensure_directory(OUTPUT_PATH)

    # Step 1: Create Spark Session
    print_section("Step 1: Initializing Spark")
    spark = create_spark_session("CarRecommendation_BEAD")

    # Step 2: Load Car Data
    print_section("Step 2: Loading Car Listings")
    car_df = load_car_data(spark, CAR_DATA_PATH)

    # Step 3: Load COE Data
    print_section("Step 3: Loading COE Data")
    coe_df = load_coe_data(spark, COE_DATA_PATH)

    # Step 4: Profile Data
    print_section("Step 4: Profiling Data")

    car_profile = profile_dataframe(car_df, "Car Listings")
    print_profile_summary(car_profile)

    coe_profile = profile_dataframe(coe_df, "COE Bidding Results")
    print_profile_summary(coe_profile)

    # Step 5: Save Parquet Files
    print_section("Step 5: Saving Parquet Files")
    save_as_parquet(car_df, os.path.join(OUTPUT_PATH, "cars.parquet"))
    save_as_parquet(coe_df, os.path.join(OUTPUT_PATH, "coe.parquet"))

    # Step 6: Generate Reports
    print_section("Step 6: Generating Reports")
    generate_profile_report(car_profile, os.path.join(OUTPUT_PATH, "car_profile_report.html"))
    generate_profile_report(coe_profile, os.path.join(OUTPUT_PATH, "coe_profile_report.html"))
    save_profile_json(car_profile, os.path.join(OUTPUT_PATH, "car_profile.json"))
    save_profile_json(coe_profile, os.path.join(OUTPUT_PATH, "coe_profile.json"))

    # Summary
    print_header("INGESTION PIPELINE COMPLETE")
    print(f"""
Outputs Generated:
------------------
1. data/processed/cars.parquet       - Spark-optimized car data
2. data/processed/coe.parquet        - Spark-optimized COE data
3. data/processed/car_profile_report.html  - Car data profile
4. data/processed/coe_profile_report.html  - COE data profile
5. data/processed/car_profile.json   - Car profile (JSON)
6. data/processed/coe_profile.json   - COE profile (JSON)

Dataset Summary:
----------------
Car Listings: {car_df.count():,} records
COE Data: {coe_df.count():,} records

Next Steps:
-----------
1. Review profile reports for data quality
2. Proceed to ML pipeline for feature engineering
3. Train CatBoost model for price prediction
""")

    # Show schema for documentation
    print_section("Car Data Schema")
    car_df.printSchema()

    print_section("COE Data Schema")
    coe_df.printSchema()

    # Stop Spark session
    spark.stop()

    return car_profile, coe_profile


if __name__ == "__main__":
    main()
