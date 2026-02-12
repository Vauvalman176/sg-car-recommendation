"""
Financial calculations for Singapore car market.
PARF rebate, COE rebate, loan details, depreciation.
Ref: https://www.lta.gov.sg/content/ltagov/en/industry_innovations/industry_matters/regulations_702.html
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, when, lit, round as spark_round, greatest
)
from pyspark.sql.types import DoubleType


# LTA PARF rebate schedule - (age_threshold, rebate_pct_of_arf)
# anything >= 10 years gets 0%
PARF_REBATE_TABLE = [
    (5, 0.75),
    (6, 0.70),
    (7, 0.65),
    (8, 0.60),
    (9, 0.55),
    (10, 0.50),
]

# MAS loan regulations
INTEREST_RATE = 0.0278      # flat rate p.a.
LOAN_TENURE_YEARS = 7
LOAN_TENURE_MONTHS = 84     # 7 * 12
OMV_THRESHOLD = 20000       # loan % depends on OMV


def calculate_parf_rebate(df: DataFrame) -> DataFrame:
    """Calculate PARF rebate = ARF * age-based percentage. Cars >10yrs get 0."""
    arf_col = col("arf").cast(DoubleType())
    age_col = col("car_age_years")

    # chain when() expressions from the rebate table
    expr = when(age_col < lit(PARF_REBATE_TABLE[0][0]),
                arf_col * lit(PARF_REBATE_TABLE[0][1]))

    for age_threshold, pct in PARF_REBATE_TABLE[1:]:
        expr = expr.when(age_col < lit(age_threshold), arf_col * lit(pct))

    expr = expr.otherwise(lit(0.0))

    df = df.withColumn("parf_rebate", spark_round(expr, 2))
    return df


def calculate_coe_rebate(df: DataFrame) -> DataFrame:
    """COE rebate = coe_paid * remaining_months / 120 (10yr COE period)."""
    coe_rebate = (
        col("coe") * greatest(col("coe_months_left"), lit(0.0)) / lit(120.0)
    )
    df = df.withColumn("coe_rebate", spark_round(coe_rebate, 2))
    return df


def calculate_scrap_value(df: DataFrame) -> DataFrame:
    """Scrap value = PARF rebate + COE rebate. Call after the two rebate functions."""
    df = df.withColumn(
        "scrap_value",
        spark_round(col("parf_rebate") + col("coe_rebate"), 2)
    )
    return df


def calculate_loan_details(df: DataFrame) -> DataFrame:
    """
    Calculate loan amount, installment, interest and downpayment.

    MAS rules: max loan 70% if OMV <= $20K, otherwise 60%.
    Monthly installment = (loan * (1 + rate * tenure)) / months
    """
    loan_pct = when(col("omv") <= lit(OMV_THRESHOLD), lit(0.70)).otherwise(lit(0.60))

    df = df.withColumn("loan_amount", spark_round(col("price") * loan_pct, 2))

    total_payable = col("loan_amount") * (lit(1.0) + lit(INTEREST_RATE) * lit(LOAN_TENURE_YEARS))

    df = df.withColumn(
        "monthly_installment",
        spark_round(total_payable / lit(LOAN_TENURE_MONTHS), 2)
    )

    df = df.withColumn(
        "total_interest",
        spark_round(total_payable - col("loan_amount"), 2)
    )

    df = df.withColumn(
        "downpayment",
        spark_round(col("price") - col("loan_amount"), 2)
    )

    return df


def calculate_monthly_depreciation(df: DataFrame) -> DataFrame:
    """Monthly depreciation = (price - scrap_value) / coe_months_left.
    Returns null for expired COE (months <= 0)."""
    df = df.withColumn(
        "monthly_depreciation",
        when(
            col("coe_months_left") > lit(0),
            spark_round(
                (col("price") - col("scrap_value")) / col("coe_months_left"),
                2
            )
        )
    )
    return df


def add_financial_columns(df: DataFrame) -> DataFrame:
    """Run all financial calculations and return df with new columns."""
    print("Calculating financial metrics...")
    df = calculate_parf_rebate(df)
    print("  PARF rebate done")
    df = calculate_coe_rebate(df)
    print("  COE rebate done")
    df = calculate_scrap_value(df)
    print("  Scrap value done")
    df = calculate_loan_details(df)
    print("  Loan details done")
    df = calculate_monthly_depreciation(df)
    print("  Depreciation done")
    return df
