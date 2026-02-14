"""
Data Ingestion Module
Loads car listings and COE data into PySpark DataFrames.
Simulates HDFS/Sqoop ingestion for academic demonstration.
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, to_date, when, lit, year, month,
    datediff, current_date, regexp_replace
)
from pyspark.sql.types import DoubleType, IntegerType
import os

from .schema import CAR_SCHEMA, COE_SCHEMA


def create_spark_session(app_name: str = "CarRecommendationSystem") -> SparkSession:
    """Create and configure a local SparkSession."""
    spark = SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .config("spark.driver.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

    # Set log level to reduce noise
    spark.sparkContext.setLogLevel("WARN")

    print(f"SparkSession created: {app_name}")
    print(f"Spark version: {spark.version}")

    return spark


def load_car_data(spark: SparkSession, file_path: str) -> DataFrame:
    """Load car listings CSV, parse dates, calculate car age, cast numeric types."""
    print(f"Loading car data from: {file_path}")

    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(file_path)

    print(f"Raw records loaded: {df.count()}")

    df = df.withColumn(
        "reg_date_parsed",
        to_date(col("reg_date"), "yyyy-MM-dd")
    )

    df = df.withColumn(
        "car_age_years",
        (datediff(current_date(), col("reg_date_parsed")) / 365.25).cast(DoubleType())
    )

    if "coe_months_left" not in df.columns:
        df = df.withColumn(
            "coe_months_left",
            ((10 * 365.25) - datediff(current_date(), col("reg_date_parsed"))) / 30.44
        )

    numeric_cols = ['price', 'curb_weight', 'power', 'road_tax', 'coe',
                    'omv', 'mileage', 'dereg_value', 'engine_cap']

    for col_name in numeric_cols:
        if col_name in df.columns:
            df = df.withColumn(col_name, col(col_name).cast(DoubleType()))

    df = df.withColumn("data_source", lit("sgcarmart"))
    df = df.withColumn("ingestion_timestamp", current_date())

    print(f"Processed records: {df.count()}")
    print(f"Columns: {len(df.columns)}")

    return df


def load_coe_data(spark: SparkSession, file_path: str) -> DataFrame:
    """Load COE bidding results CSV into Spark DataFrame."""
    print(f"Loading COE data from: {file_path}")

    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(file_path)

    print(f"Raw COE records loaded: {df.count()}")

    df = df.withColumn("coe_year", year(to_date(col("month"), "yyyy-MM")))
    df = df.withColumn("coe_month", month(to_date(col("month"), "yyyy-MM")))
    df = df.withColumn("premium", col("premium").cast(IntegerType()))
    df = df.withColumn("ingestion_timestamp", current_date())

    print(f"Processed COE records: {df.count()}")

    return df


def save_as_parquet(df: DataFrame, output_path: str, partition_by: str = None):
    """Save DataFrame as Parquet format."""
    print(f"Saving to Parquet: {output_path}")

    writer = df.write.mode("overwrite")

    if partition_by:
        writer = writer.partitionBy(partition_by)

    writer.parquet(output_path)

    print(f"Saved successfully: {output_path}")


def run_ingestion_pipeline(base_path: str):
    """Run complete ingestion: load CSVs, process, save as parquet."""
    print("="*60)
    print("DATA INGESTION PIPELINE")
    print("="*60)

    # Create Spark session
    spark = create_spark_session()

    # Define file paths
    car_data_path = os.path.join(
        base_path,
        "webscrap_sgcarmart/data/carlist_20260128_with_loan_info.csv"
    )
    coe_data_path = os.path.join(
        base_path,
        "data/coe/coe_bidding_results.csv"
    )
    output_path = os.path.join(base_path, "data/processed")

    # Create output directory
    os.makedirs(output_path, exist_ok=True)

    # Load and process car data
    print("\n" + "-"*40)
    print("Step 1: Loading Car Listings")
    print("-"*40)
    car_df = load_car_data(spark, car_data_path)

    # Load and process COE data
    print("\n" + "-"*40)
    print("Step 2: Loading COE Data")
    print("-"*40)
    coe_df = load_coe_data(spark, coe_data_path)

    # Save as Parquet
    print("\n" + "-"*40)
    print("Step 3: Saving as Parquet")
    print("-"*40)
    save_as_parquet(car_df, os.path.join(output_path, "cars.parquet"))
    save_as_parquet(coe_df, os.path.join(output_path, "coe.parquet"))

    # Print summary
    print("\n" + "="*60)
    print("INGESTION COMPLETE")
    print("="*60)
    print(f"Car listings: {car_df.count()} records")
    print(f"COE data: {coe_df.count()} records")
    print(f"Output: {output_path}")

    # Show sample data
    print("\n" + "-"*40)
    print("Sample Car Data:")
    print("-"*40)
    car_df.select("carmodel", "price", "car_age_years", "coe_months_left", "type_of_vehicle").show(5, truncate=False)

    print("\n" + "-"*40)
    print("Sample COE Data:")
    print("-"*40)
    coe_df.select("month", "vehicle_class", "premium", "quota").show(5)

    # Return DataFrames for further processing
    return spark, car_df, coe_df


if __name__ == "__main__":
    # Run pipeline when executed directly
    base_path = "/Users/jai/Downloads/bigdata_project"
    run_ingestion_pipeline(base_path)
