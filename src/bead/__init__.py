"""
Data ingestion & profiling module.
Handles data loading, schema validation, and profiling for the car recommendation system.
"""

from .schema import CAR_SCHEMA, COE_SCHEMA
from .ingest import load_car_data, load_coe_data, create_spark_session
from .profiler import profile_dataframe, generate_profile_report

__all__ = [
    'CAR_SCHEMA',
    'COE_SCHEMA',
    'load_car_data',
    'load_coe_data',
    'create_spark_session',
    'profile_dataframe',
    'generate_profile_report'
]
