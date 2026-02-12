"""
Hard constraint filters for narrowing down candidate cars.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col


def filter_by_vehicle_type(df, vehicle_type):
    """Filter by type_of_vehicle column."""
    return df.filter(col("type_of_vehicle") == vehicle_type)


def filter_by_coe_remaining(df, min_months=60):
    """Keep only cars with at least min_months of COE left."""
    return df.filter(col("coe_months_left") >= min_months)


def filter_by_budget(df, max_monthly):
    """Filter by monthly installment ceiling."""
    return df.filter(col("monthly_installment") <= max_monthly)


def filter_by_price_range(df, max_price):
    """Filter by max listing price."""
    return df.filter(col("price") <= max_price)


def apply_all_filters(df, constraints):
    """
    Chain all applicable filters based on constraints dict.
    Prints remaining count after each filter step.

    constraints keys: vehicle_type, min_coe_months, max_monthly_budget, max_price
    """
    print(f"  Starting candidates: {df.count():,}")

    vehicle_type = constraints.get("vehicle_type")
    if vehicle_type:
        df = filter_by_vehicle_type(df, vehicle_type)
        print(f"  After vehicle type = {vehicle_type}: {df.count():,}")

    min_coe = constraints.get("min_coe_months", 60)
    if min_coe:
        df = filter_by_coe_remaining(df, min_coe)
        print(f"  After COE >= {min_coe} months: {df.count():,}")

    max_monthly = constraints.get("max_monthly_budget")
    if max_monthly:
        df = filter_by_budget(df, max_monthly)
        print(f"  After monthly <= ${max_monthly:,.0f}: {df.count():,}")

    max_price = constraints.get("max_price")
    if max_price:
        df = filter_by_price_range(df, max_price)
        print(f"  After price <= ${max_price:,.0f}: {df.count():,}")

    print(f"  Final candidates: {df.count():,}")
    return df
