"""
Feature engineering for car price prediction.
Imputation, derived features, and PySpark ML Pipeline (StringIndexer -> OHE -> VectorAssembler -> Scaler).
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, when, lit, coalesce, date_format,
    avg, greatest, percentile_approx
)
from pyspark.sql.types import DoubleType
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    StringIndexer, OneHotEncoder,
    VectorAssembler, StandardScaler
)
from typing import Tuple, List


NUMERIC_FEATURE_COLS = [
    "engine_cap", "power", "curb_weight", "mileage",
    "coe", "omv", "arf_double", "road_tax", "owners",
    "car_age_years", "coe_months_left",
]

CATEGORICAL_FEATURE_COLS = ["transmission", "fuel_type", "type_of_vehicle"]

ENGINEERED_FEATURE_COLS = ["mileage_per_year", "power_to_weight", "coe_premium_at_reg"]

# these columns have significant nulls (>5%) from profiling
IMPUTE_COLS = ["mileage", "power", "road_tax", "engine_cap", "curb_weight", "coe"]

TARGET_COL = "price"


def filter_valid_records(df: DataFrame) -> DataFrame:
    """Remove rows with null/invalid price or negative car age."""
    before_count = df.count()
    print(f"Records before filtering: {before_count:,}")

    df = df.filter(
        col("price").isNotNull() &
        (col("price") > 0) &
        col("car_age_years").isNotNull() &
        (col("car_age_years") >= 0)
    )

    after_count = df.count()
    print(f"Records after filtering: {after_count:,}")
    print(f"  Removed: {before_count - after_count:,} invalid records")

    return df


def impute_missing_values(df: DataFrame) -> DataFrame:
    """
    Median-by-vehicle-type imputation for columns with significant nulls.
    Falls back to global median if the group median is null.
    """
    print("Imputing missing values...")

    for col_name in IMPUTE_COLS:
        if col_name not in df.columns:
            continue

        null_count = df.filter(col(col_name).isNull()).count()
        if null_count == 0:
            continue

        # group medians by vehicle type
        group_medians = df.groupBy("type_of_vehicle").agg(
            percentile_approx(col_name, 0.5, 100).alias(f"{col_name}_median")
        )

        global_median_row = df.select(
            percentile_approx(col_name, 0.5, 100).alias("global_median")
        ).collect()[0]
        global_median = global_median_row["global_median"]

        df = df.join(group_medians, on="type_of_vehicle", how="left")

        # priority: original value -> group median -> global median
        df = df.withColumn(
            col_name,
            coalesce(
                col(col_name),
                col(f"{col_name}_median"),
                lit(global_median)
            )
        )
        df = df.drop(f"{col_name}_median")

        print(f"  {col_name}: filled {null_count:,} nulls (median={global_median})")

    return df


def join_coe_premium(car_df: DataFrame, coe_df: DataFrame) -> DataFrame:
    """
    Join the COE premium at time of registration to each car.
    Uses Category B average premium for the registration month.
    Unmatched cars get the global median as fallback.
    """
    print("Joining COE premium at registration...")

    # Cat B covers most passenger cars
    coe_cat_b = coe_df.filter(col("vehicle_class") == "Category B")

    coe_monthly = coe_cat_b.groupBy("month").agg(
        avg("premium").alias("coe_premium_at_reg")
    )

    car_df = car_df.withColumn(
        "reg_year_month",
        date_format(col("reg_date_parsed"), "yyyy-MM")
    )

    car_df = car_df.join(
        coe_monthly,
        car_df["reg_year_month"] == coe_monthly["month"],
        how="left"
    ).drop(coe_monthly["month"])

    # fallback for cars where we don't have COE data for that month
    global_median_premium = coe_cat_b.select(
        percentile_approx("premium", 0.5, 100).alias("median_prem")
    ).collect()[0]["median_prem"]

    car_df = car_df.withColumn(
        "coe_premium_at_reg",
        coalesce(col("coe_premium_at_reg"), lit(float(global_median_premium)))
    )

    matched = car_df.filter(col("reg_year_month").isNotNull()).count()
    unmatched = car_df.filter(col("coe_premium_at_reg") == float(global_median_premium)).count()
    print(f"  Matched {matched:,} cars, {unmatched:,} used median fallback (${global_median_premium:,})")

    car_df = car_df.drop("reg_year_month")
    return car_df


def create_engineered_features(df: DataFrame) -> DataFrame:
    """Add derived features: mileage_per_year, power_to_weight, arf_double."""
    print("Creating engineered features...")

    # arf needs to be double for VectorAssembler
    df = df.withColumn("arf_double", col("arf").cast(DoubleType()))

    df = df.withColumn(
        "mileage_per_year",
        col("mileage") / greatest(col("car_age_years"), lit(0.5))
    )
    df = df.withColumn(
        "power_to_weight",
        col("power") / greatest(col("curb_weight"), lit(1.0))
    )

    print("  Added: arf_double, mileage_per_year, power_to_weight")
    return df


def build_feature_pipeline() -> Pipeline:
    """
    Build the ML feature pipeline:
    StringIndexer -> OneHotEncoder -> VectorAssembler -> StandardScaler
    """
    stages = []

    # index categorical columns
    indexer_output_cols = []
    for cat_col in CATEGORICAL_FEATURE_COLS:
        indexer = StringIndexer(
            inputCol=cat_col,
            outputCol=f"{cat_col}_index",
            handleInvalid="keep"
        )
        stages.append(indexer)
        indexer_output_cols.append(f"{cat_col}_index")

    # one-hot encode
    encoder_output_cols = [f"{c}_vec" for c in CATEGORICAL_FEATURE_COLS]
    encoder = OneHotEncoder(
        inputCols=indexer_output_cols,
        outputCols=encoder_output_cols
    )
    stages.append(encoder)

    # assemble everything into a single feature vector
    assembler_input_cols = NUMERIC_FEATURE_COLS + ENGINEERED_FEATURE_COLS + encoder_output_cols
    assembler = VectorAssembler(
        inputCols=assembler_input_cols,
        outputCol="features_unscaled",
        handleInvalid="skip"
    )
    stages.append(assembler)

    # NOTE: withMean=False because OHE produces sparse vectors and centering would densify them
    scaler = StandardScaler(
        inputCol="features_unscaled",
        outputCol="features",
        withStd=True,
        withMean=False
    )
    stages.append(scaler)

    pipeline = Pipeline(stages=stages)
    print(f"Pipeline: {len(stages)} stages, {len(NUMERIC_FEATURE_COLS)} numeric + "
          f"{len(ENGINEERED_FEATURE_COLS)} engineered + {len(CATEGORICAL_FEATURE_COLS)} categorical features")

    return pipeline


def get_feature_names() -> List[str]:
    """Get ordered feature names matching the VectorAssembler output."""
    names = list(NUMERIC_FEATURE_COLS) + list(ENGINEERED_FEATURE_COLS)
    for cat_col in CATEGORICAL_FEATURE_COLS:
        names.append(f"{cat_col}_vec")
    return names


def transform_features(car_df: DataFrame, coe_df: DataFrame) -> Tuple[DataFrame, object]:
    """
    Full feature engineering pipeline: filter -> impute -> join COE -> engineer -> ML pipeline.
    Returns the transformed df and the fitted pipeline model.
    """
    print("Starting feature engineering...")

    df = filter_valid_records(car_df)
    df = impute_missing_values(df)
    df = join_coe_premium(df, coe_df)
    df = create_engineered_features(df)

    pipeline = build_feature_pipeline()
    pipeline_model = pipeline.fit(df)
    transformed_df = pipeline_model.transform(df)

    print(f"Feature engineering complete: {transformed_df.count():,} records")
    return transformed_df, pipeline_model
