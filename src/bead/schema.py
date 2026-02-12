"""
Schema definitions for car listings and COE data.
Defines PySpark StructType schemas for data validation.
"""

from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    FloatType, DoubleType, DateType, BooleanType
)

# Schema for car listings data
CAR_SCHEMA = StructType([
    StructField("price", DoubleType(), True),
    StructField("transmission", StringType(), True),
    StructField("fuel_type", StringType(), True),
    StructField("curb_weight", DoubleType(), True),
    StructField("power", DoubleType(), True),
    StructField("road_tax", DoubleType(), True),
    StructField("coe", DoubleType(), True),
    StructField("omv", DoubleType(), True),
    StructField("arf", IntegerType(), True),
    StructField("mileage", DoubleType(), True),
    StructField("owners", DoubleType(), True),
    StructField("dealer", StringType(), True),
    StructField("dereg_value", DoubleType(), True),
    StructField("engine_cap", DoubleType(), True),
    StructField("reg_date", StringType(), True),  # Will be converted to date
    StructField("carmodel", StringType(), True),
    StructField("type_of_vehicle", StringType(), True),
    StructField("url", StringType(), True),
    # Enriched fields from loan analysis
    StructField("coe_expiry", StringType(), True),
    StructField("coe_months_left", DoubleType(), True),
    StructField("max_loan_months", DoubleType(), True),
    StructField("min_downpayment_pct", DoubleType(), True),
    StructField("max_loan_pct", DoubleType(), True),
    StructField("can_loan_full_coe", BooleanType(), True),
])

# Schema for COE bidding results data
COE_SCHEMA = StructType([
    StructField("_id", IntegerType(), True),
    StructField("month", StringType(), True),  # Format: YYYY-MM
    StructField("bidding_no", IntegerType(), True),
    StructField("vehicle_class", StringType(), True),
    StructField("quota", IntegerType(), True),
    StructField("bids_success", IntegerType(), True),
    StructField("bids_received", IntegerType(), True),
    StructField("premium", IntegerType(), True),
])

# Column descriptions for documentation
CAR_COLUMNS_DESC = {
    "price": "Listed selling price in SGD",
    "transmission": "Auto or Manual",
    "fuel_type": "Petrol, Diesel, Electric, Petrol-Electric, Diesel-Electric",
    "curb_weight": "Vehicle weight in kg",
    "power": "Engine power in bhp",
    "road_tax": "Annual road tax in SGD",
    "coe": "COE price paid at registration in SGD",
    "omv": "Open Market Value in SGD",
    "arf": "Additional Registration Fee in SGD",
    "mileage": "Odometer reading in km",
    "owners": "Number of previous owners",
    "dealer": "Dealer/seller name",
    "dereg_value": "Deregistration value (PARF + COE rebate) in SGD",
    "engine_cap": "Engine capacity in cc",
    "reg_date": "First registration date",
    "carmodel": "Make and model name",
    "type_of_vehicle": "Vehicle category (SUV, Sedan, etc.)",
    "url": "Source listing URL",
    "coe_expiry": "COE expiry date (10 years from reg_date)",
    "coe_months_left": "Months remaining on COE",
    "max_loan_months": "Maximum loan tenure in months",
    "min_downpayment_pct": "Minimum downpayment percentage (30% or 40%)",
    "max_loan_pct": "Maximum loan-to-value percentage",
    "can_loan_full_coe": "Whether loan can cover full remaining COE period",
}

COE_COLUMNS_DESC = {
    "_id": "Record ID",
    "month": "Bidding month (YYYY-MM)",
    "bidding_no": "Bidding round (1 or 2)",
    "vehicle_class": "COE category (A, B, C, D, E)",
    "quota": "Number of COEs available",
    "bids_success": "Number of successful bids",
    "bids_received": "Total bids received",
    "premium": "COE premium (winning bid price) in SGD",
}
