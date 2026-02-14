"""
FastAPI server for the car recommendation system.
Run: uvicorn api.main:app --port 8000
Docs: http://localhost:8000/docs
"""

import sys
import os
import math
import numpy as np
import pandas as pd
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field

# add src/ to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREDICTIONS_PATH = os.path.join(BASE_PATH, "data/pbda_output/predictions.parquet")

# global - loaded once at startup
cars_df: pd.DataFrame = None


# ──────────────────────────── Pydantic models ────────────────────────────

class UserCar(BaseModel):
    carmodel: str = Field(..., example="Honda Vezel 1.5A")
    type_of_vehicle: str = Field("SUV", example="SUV")
    engine_cap: float = Field(..., example=1496)
    power: float = Field(..., example=131)
    curb_weight: float = Field(..., example=1310)
    mileage: float = Field(..., example=80000)
    price: float = Field(..., example=85000)
    car_age_years: float = Field(..., example=6.0)
    coe_months_left: float = Field(..., example=48)
    arf: float = Field(..., example=15000)
    coe: float = Field(..., example=50000)
    omv: float = Field(20000, example=22000)


class Constraints(BaseModel):
    vehicle_type: Optional[str] = Field(None, example="SUV")
    min_coe_months: Optional[int] = Field(60, example=60)
    max_monthly_budget: Optional[float] = Field(None, example=1500)
    max_price: Optional[float] = Field(None, example=250000)


class RecommendRequest(BaseModel):
    user_car: UserCar
    constraints: Constraints = Constraints()
    top_k: int = Field(5, ge=1, le=20)


class ExploreRequest(BaseModel):
    user_car: UserCar
    target_type: str = Field(..., example="Luxury Sedan")
    max_budget: Optional[float] = Field(None, example=200000)
    top_k: int = Field(5, ge=1, le=20)


class ScrapValueRequest(BaseModel):
    arf: float = Field(..., example=15000)
    car_age_years: float = Field(..., example=6.0)
    coe: float = Field(..., example=50000)
    coe_months_left: float = Field(..., example=48)


class FinancialRequest(BaseModel):
    price: float = Field(..., example=85000)
    arf: float = Field(..., example=15000)
    car_age_years: float = Field(..., example=6.0)
    coe: float = Field(..., example=50000)
    coe_months_left: float = Field(..., example=48)
    omv: float = Field(..., example=22000)


# ──────────────────────────── helpers ────────────────────────────

def clean_val(v):
    """Convert NaN/inf to None for JSON serialization."""
    if v is None:
        return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def row_to_dict(row):
    """Convert a pandas row to a JSON-safe dict."""
    d = row.to_dict() if hasattr(row, 'to_dict') else dict(row)
    return {k: clean_val(v) for k, v in d.items()}


# financial constants (same as financial.py)
INTEREST_RATE = 0.0278
LOAN_TENURE_YEARS = 7
LOAN_TENURE_MONTHS = 84
OMV_THRESHOLD = 20000

# PARF rebate table
PARF_REBATE_TABLE = [
    (5, 0.75), (6, 0.70), (7, 0.65),
    (8, 0.60), (9, 0.55), (10, 0.50),
]

# similarity features
SIMILARITY_FEATURES = ["engine_cap", "power", "curb_weight", "mileage", "car_age_years"]


def calc_scrap_value(arf, car_age_years, coe, coe_months_left):
    """Pure Python scrap value calculation."""
    parf_rebate = 0.0
    for threshold, pct in PARF_REBATE_TABLE:
        if car_age_years < threshold:
            parf_rebate = arf * pct
            break

    coe_rebate = coe * max(coe_months_left, 0) / 120.0
    return {
        "parf_rebate": round(parf_rebate, 2),
        "coe_rebate": round(coe_rebate, 2),
        "scrap_value": round(parf_rebate + coe_rebate, 2),
    }


def filter_candidates(df, constraints):
    """Apply constraint filters on pandas DataFrame."""
    filtered = df.copy()
    steps = [f"Starting candidates: {len(filtered):,}"]

    vtype = constraints.get("vehicle_type")
    if vtype:
        filtered = filtered[filtered["type_of_vehicle"].str.lower() == vtype.lower()]
        steps.append(f"After vehicle type = {vtype}: {len(filtered):,}")

    min_coe = constraints.get("min_coe_months")
    if min_coe:
        filtered = filtered[filtered["coe_months_left"] >= min_coe]
        steps.append(f"After COE >= {min_coe} months: {len(filtered):,}")

    max_monthly = constraints.get("max_monthly_budget")
    if max_monthly:
        filtered = filtered[filtered["monthly_installment"] <= max_monthly]
        steps.append(f"After monthly <= ${max_monthly:,.0f}: {len(filtered):,}")

    max_price = constraints.get("max_price")
    if max_price:
        filtered = filtered[filtered["price"] <= max_price]
        steps.append(f"After price <= ${max_price:,.0f}: {len(filtered):,}")

    steps.append(f"Final candidates: {len(filtered):,}")
    return filtered, steps


def compute_similarity(user_car, candidates_df, features):
    """Cosine similarity between user car and all candidates using pandas/numpy."""
    # min-max normalize
    mins = candidates_df[features].min()
    maxs = candidates_df[features].max()
    ranges = maxs - mins
    ranges = ranges.replace(0, 1)  # avoid div by zero

    # normalize candidates
    norm_candidates = (candidates_df[features] - mins) / ranges

    # normalize user vector
    user_vals = np.array([float(user_car.get(f, 0)) for f in features])
    norm_user = (user_vals - mins.values) / ranges.values

    # cosine similarity
    user_norm = np.linalg.norm(norm_user)
    if user_norm == 0:
        candidates_df = candidates_df.copy()
        candidates_df["similarity_score"] = 0.0
        return candidates_df

    scores = []
    for _, row in norm_candidates.iterrows():
        cand = row.values
        cand_norm = np.linalg.norm(cand)
        if cand_norm == 0:
            scores.append(0.0)
        else:
            sim = np.dot(norm_user, cand) / (user_norm * cand_norm)
            scores.append(round(float(np.clip(sim, 0, 1)), 4))

    candidates_df = candidates_df.copy()
    candidates_df["similarity_score"] = scores
    return candidates_df


# ──────────────────────────── startup ────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global cars_df

    # load parquet directly with pandas (no Spark needed!)
    print(f"Loading predictions from {PREDICTIONS_PATH}")
    cars_df = pd.read_parquet(PREDICTIONS_PATH)
    print(f"Ready! {len(cars_df):,} cars loaded.")

    yield


app = FastAPI(
    title="SG Car Recommendation API",
    description="Enter your car details, get trade-in value and recommendations.",
    version="1.0.0",
    lifespan=lifespan,
)


# ──────────────────────────── endpoints ────────────────────────────

@app.get("/")
def root():
    return {
        "service": "SG Car Recommendation API",
        "cars_loaded": len(cars_df) if cars_df is not None else 0,
        "docs": "/docs",
    }


@app.get("/stats")
def dataset_stats():
    """Dataset summary: counts, vehicle types, price range."""
    return {
        "total_cars": len(cars_df),
        "vehicle_types": sorted(cars_df["type_of_vehicle"].dropna().unique().tolist()),
        "price_range": {
            "min": float(cars_df["price"].min()),
            "max": float(cars_df["price"].max()),
            "mean": round(float(cars_df["price"].mean()), 2),
        },
        "anomaly_breakdown": cars_df["anomaly_flag"].value_counts().to_dict(),
    }


@app.get("/cars")
def list_cars(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    vehicle_type: Optional[str] = None,
    max_price: Optional[float] = None,
    anomaly_flag: Optional[str] = None,
    sort_by: str = Query("price"),
    sort_order: str = Query("asc"),
):
    """Browse cars with pagination and filters."""
    df = cars_df.copy()

    if vehicle_type:
        df = df[df["type_of_vehicle"].str.lower() == vehicle_type.lower()]
    if max_price:
        df = df[df["price"] <= max_price]
    if anomaly_flag:
        df = df[df["anomaly_flag"] == anomaly_flag]

    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=(sort_order == "asc"), na_position="last")

    total = len(df)
    start = (page - 1) * page_size
    page_df = df.iloc[start:start + page_size]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "cars": [row_to_dict(row) for _, row in page_df.iterrows()],
    }


@app.get("/cars/{car_id}")
def get_car(car_id: int):
    """Get a single car by row index."""
    if car_id < 0 or car_id >= len(cars_df):
        raise HTTPException(404, f"Car {car_id} not found. Valid range: 0-{len(cars_df)-1}")
    row = cars_df.iloc[car_id]
    return row_to_dict(row)


@app.post("/scrap-value")
def scrap_value(req: ScrapValueRequest):
    """Calculate trade-in value (PARF rebate + COE rebate)."""
    return calc_scrap_value(req.arf, req.car_age_years, req.coe, req.coe_months_left)


@app.post("/financial-profile")
def financial_profile(req: FinancialRequest):
    """Full financial breakdown: scrap value + loan details + depreciation."""
    scrap = calc_scrap_value(req.arf, req.car_age_years, req.coe, req.coe_months_left)

    loan_pct = 0.70 if req.omv <= OMV_THRESHOLD else 0.60
    loan_amount = round(req.price * loan_pct, 2)
    total_payable = loan_amount * (1.0 + INTEREST_RATE * LOAN_TENURE_YEARS)
    monthly_installment = round(total_payable / LOAN_TENURE_MONTHS, 2)
    total_interest = round(total_payable - loan_amount, 2)
    downpayment = round(req.price - loan_amount, 2)

    monthly_dep = None
    if req.coe_months_left > 0:
        monthly_dep = round((req.price - scrap["scrap_value"]) / req.coe_months_left, 2)

    return {
        "scrap_value": scrap,
        "loan": {
            "loan_percent": loan_pct,
            "loan_amount": loan_amount,
            "downpayment": downpayment,
            "monthly_installment": monthly_installment,
            "total_interest": total_interest,
            "tenure_months": LOAN_TENURE_MONTHS,
        },
        "monthly_depreciation": monthly_dep,
    }


@app.post("/recommend")
def get_recommendations(req: RecommendRequest):
    """Get top-K car recommendations based on your car and budget constraints."""
    user_car = req.user_car.model_dump()
    constraints = req.constraints.model_dump()

    # scrap value
    scrap = calc_scrap_value(
        user_car["arf"], user_car["car_age_years"],
        user_car["coe"], user_car["coe_months_left"]
    )

    # filter
    filtered, filter_steps = filter_candidates(cars_df, constraints)

    if len(filtered) == 0:
        return {
            "user_summary": {"carmodel": user_car["carmodel"], **scrap},
            "constraints": constraints,
            "total_candidates": 0,
            "filter_steps": filter_steps,
            "recommendations": [],
            "generated_at": datetime.now().isoformat(),
        }

    # similarity
    scored = compute_similarity(user_car, filtered, SIMILARITY_FEATURES)
    top_k = scored.nlargest(req.top_k, "similarity_score")

    # build results
    recommendations = []
    for rank, (_, row) in enumerate(top_k.iterrows(), 1):
        recommendations.append({
            "rank": rank,
            "carmodel": str(row.get("carmodel", "")),
            "price": clean_val(float(row.get("price", 0))),
            "predicted_price": clean_val(float(row.get("predicted_price", 0))),
            "similarity_score": float(row.get("similarity_score", 0)),
            "net_upgrade_cost": round(float(row.get("price", 0)) - scrap["scrap_value"], 2),
            "monthly_installment": clean_val(float(row.get("monthly_installment", 0))),
            "coe_months_left": clean_val(float(row.get("coe_months_left", 0))),
            "anomaly_flag": str(row.get("anomaly_flag", "")),
            "type_of_vehicle": str(row.get("type_of_vehicle", "")),
            "engine_cap": clean_val(float(row.get("engine_cap", 0))),
            "power": clean_val(float(row.get("power", 0))),
            "mileage": clean_val(float(row.get("mileage", 0))),
            "transmission": str(row.get("transmission", "")),
            "fuel_type": str(row.get("fuel_type", "")),
            "dealer": str(row.get("dealer", "")),
            "url": str(row.get("url", "")),
        })

    return {
        "user_summary": {
            "carmodel": user_car["carmodel"],
            **scrap,
            "car_age_years": user_car["car_age_years"],
            "coe_months_left": user_car["coe_months_left"],
        },
        "constraints": constraints,
        "total_candidates": len(filtered),
        "filter_steps": filter_steps,
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat(),
    }


@app.post("/explore")
def explore_category(req: ExploreRequest):
    """Switch categories: find the most similar cars in a different vehicle type.
    E.g. you have a Honda Vezel (SUV) and want to explore Luxury Sedans."""
    user_car = req.user_car.model_dump()

    # trade-in value
    scrap = calc_scrap_value(
        user_car["arf"], user_car["car_age_years"],
        user_car["coe"], user_car["coe_months_left"]
    )

    # filter to target type
    filtered = cars_df[cars_df["type_of_vehicle"].str.lower() == req.target_type.lower()].copy()
    if req.max_budget:
        filtered = filtered[filtered["price"] <= req.max_budget]

    available_types = sorted(cars_df["type_of_vehicle"].dropna().unique().tolist())

    if len(filtered) == 0:
        return {
            "user_summary": {"carmodel": user_car["carmodel"], **scrap},
            "target_type": req.target_type,
            "max_budget": req.max_budget,
            "total_in_category": 0,
            "message": f"No cars found for '{req.target_type}'. Available types: {available_types}",
            "recommendations": [],
            "generated_at": datetime.now().isoformat(),
        }

    # similarity
    scored = compute_similarity(user_car, filtered, SIMILARITY_FEATURES)
    top_k = scored.nlargest(req.top_k, "similarity_score")

    recommendations = []
    for rank, (_, row) in enumerate(top_k.iterrows(), 1):
        car_price = float(row.get("price", 0))
        net_cost = round(car_price - scrap["scrap_value"], 2)
        recommendations.append({
            "rank": rank,
            "carmodel": str(row.get("carmodel", "")),
            "price": clean_val(car_price),
            "predicted_price": clean_val(float(row.get("predicted_price", 0))),
            "similarity_score": float(row.get("similarity_score", 0)),
            "trade_in_discount": scrap["scrap_value"],
            "estimated_cost_after_tradein": net_cost,
            "monthly_installment": clean_val(float(row.get("monthly_installment", 0))),
            "coe_months_left": clean_val(float(row.get("coe_months_left", 0))),
            "anomaly_flag": str(row.get("anomaly_flag", "")),
            "engine_cap": clean_val(float(row.get("engine_cap", 0))),
            "power": clean_val(float(row.get("power", 0))),
            "mileage": clean_val(float(row.get("mileage", 0))),
            "transmission": str(row.get("transmission", "")),
            "fuel_type": str(row.get("fuel_type", "")),
            "dealer": str(row.get("dealer", "")),
            "url": str(row.get("url", "")),
        })

    return {
        "user_summary": {
            "carmodel": user_car["carmodel"],
            "current_type": user_car["type_of_vehicle"],
            **scrap,
        },
        "target_type": req.target_type,
        "max_budget": req.max_budget,
        "total_in_category": len(filtered),
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat(),
    }
