"""
Data Profiler Module
Generates data quality reports and statistics for ingested data.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, count, when, isnan, isnull, mean, stddev,
    min, max, approx_count_distinct, percentile_approx
)
from pyspark.sql.types import NumericType, StringType
import json
import os
from datetime import datetime


def profile_dataframe(df: DataFrame, name: str = "DataFrame") -> dict:
    """Profile a DataFrame: null counts, distinct values, numeric stats, top categories."""
    print(f"Profiling: {name}")

    total_rows = df.count()
    total_cols = len(df.columns)

    profile = {
        "name": name,
        "profiled_at": datetime.now().isoformat(),
        "total_rows": total_rows,
        "total_columns": total_cols,
        "columns": {}
    }

    # Profile each column
    for col_name in df.columns:
        col_type = str(df.schema[col_name].dataType)
        col_profile = {
            "data_type": col_type,
            "null_count": 0,
            "null_percentage": 0.0,
            "distinct_count": 0,
        }

        # Count nulls
        null_count = df.filter(
            col(col_name).isNull() | isnan(col(col_name))
        ).count() if "double" in col_type.lower() or "float" in col_type.lower() else \
            df.filter(col(col_name).isNull()).count()

        col_profile["null_count"] = null_count
        col_profile["null_percentage"] = round((null_count / total_rows) * 100, 2) if total_rows > 0 else 0

        # Distinct count (approximate for efficiency)
        col_profile["distinct_count"] = df.select(approx_count_distinct(col_name)).collect()[0][0]

        # Numeric stats
        if "double" in col_type.lower() or "int" in col_type.lower() or "float" in col_type.lower():
            stats = df.select(
                mean(col_name).alias("mean"),
                stddev(col_name).alias("stddev"),
                min(col_name).alias("min"),
                max(col_name).alias("max")
            ).collect()[0]

            col_profile["mean"] = round(stats["mean"], 2) if stats["mean"] else None
            col_profile["stddev"] = round(stats["stddev"], 2) if stats["stddev"] else None
            col_profile["min"] = stats["min"]
            col_profile["max"] = stats["max"]

            # Percentiles
            percentiles = df.select(
                percentile_approx(col_name, [0.25, 0.5, 0.75], 100).alias("percentiles")
            ).collect()[0]["percentiles"]

            if percentiles:
                col_profile["percentile_25"] = percentiles[0]
                col_profile["percentile_50"] = percentiles[1]
                col_profile["percentile_75"] = percentiles[2]

        # String/categorical stats
        elif "string" in col_type.lower():
            # Top values
            top_values = df.groupBy(col_name) \
                .count() \
                .orderBy(col("count").desc()) \
                .limit(5) \
                .collect()

            col_profile["top_values"] = [
                {"value": row[col_name], "count": row["count"]}
                for row in top_values
            ]

        profile["columns"][col_name] = col_profile

    return profile


def print_profile_summary(profile: dict):
    """Print a formatted profile summary to console."""
    print("\n" + "="*70)
    print(f"DATA PROFILE: {profile['name']}")
    print("="*70)
    print(f"Total Rows: {profile['total_rows']:,}")
    print(f"Total Columns: {profile['total_columns']}")
    print(f"Profiled At: {profile['profiled_at']}")

    print("\n" + "-"*70)
    print(f"{'Column':<25} {'Type':<15} {'Nulls':<12} {'Distinct':<10}")
    print("-"*70)

    for col_name, col_stats in profile['columns'].items():
        null_pct = f"{col_stats['null_percentage']}%"
        print(f"{col_name[:24]:<25} {col_stats['data_type'][:14]:<15} {null_pct:<12} {col_stats['distinct_count']:<10}")

    # Highlight columns with high null rates
    high_null_cols = [
        (name, stats['null_percentage'])
        for name, stats in profile['columns'].items()
        if stats['null_percentage'] > 5
    ]

    if high_null_cols:
        print("\n" + "-"*70)
        print("COLUMNS WITH >5% NULL VALUES:")
        print("-"*70)
        for col_name, null_pct in sorted(high_null_cols, key=lambda x: -x[1]):
            print(f"  {col_name}: {null_pct}%")


def generate_profile_report(profile: dict, output_path: str):
    """Generate HTML data quality report from profile dict."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Data Profile Report - {profile['name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; flex: 1; text-align: center; }}
        .summary-card h3 {{ margin: 0; color: #4CAF50; font-size: 2em; }}
        .summary-card p {{ margin: 5px 0 0 0; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #4CAF50; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
        .null-high {{ color: #e74c3c; font-weight: bold; }}
        .null-low {{ color: #27ae60; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; }}
        .badge-numeric {{ background: #3498db; color: white; }}
        .badge-string {{ background: #9b59b6; color: white; }}
        .badge-date {{ background: #e67e22; color: white; }}
        .badge-bool {{ background: #1abc9c; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Profile Report</h1>
        <p><strong>Dataset:</strong> {profile['name']}</p>
        <p><strong>Generated:</strong> {profile['profiled_at']}</p>

        <div class="summary">
            <div class="summary-card">
                <h3>{profile['total_rows']:,}</h3>
                <p>Total Rows</p>
            </div>
            <div class="summary-card">
                <h3>{profile['total_columns']}</h3>
                <p>Total Columns</p>
            </div>
            <div class="summary-card">
                <h3>{sum(1 for c in profile['columns'].values() if c['null_percentage'] > 0)}</h3>
                <p>Columns with Nulls</p>
            </div>
        </div>

        <h2>Column Details</h2>
        <table>
            <tr>
                <th>Column</th>
                <th>Type</th>
                <th>Nulls</th>
                <th>Distinct</th>
                <th>Min</th>
                <th>Max</th>
                <th>Mean</th>
            </tr>
"""

    for col_name, stats in profile['columns'].items():
        null_class = "null-high" if stats['null_percentage'] > 5 else "null-low"
        dtype = stats['data_type'].lower()

        if 'int' in dtype or 'double' in dtype or 'float' in dtype:
            badge_class = "badge-numeric"
            dtype_label = "Numeric"
        elif 'string' in dtype:
            badge_class = "badge-string"
            dtype_label = "String"
        elif 'date' in dtype:
            badge_class = "badge-date"
            dtype_label = "Date"
        elif 'bool' in dtype:
            badge_class = "badge-bool"
            dtype_label = "Boolean"
        else:
            badge_class = "badge-string"
            dtype_label = dtype[:10]

        html += f"""
            <tr>
                <td><strong>{col_name}</strong></td>
                <td><span class="badge {badge_class}">{dtype_label}</span></td>
                <td class="{null_class}">{stats['null_percentage']}%</td>
                <td>{stats['distinct_count']:,}</td>
                <td>{stats.get('min', '-')}</td>
                <td>{stats.get('max', '-')}</td>
                <td>{stats.get('mean', '-')}</td>
            </tr>
"""

    html += """
        </table>
    </div>
</body>
</html>
"""

    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Profile report saved: {output_path}")


def save_profile_json(profile: dict, output_path: str):
    """Save profile dict as JSON."""
    with open(output_path, 'w') as f:
        json.dump(profile, f, indent=2, default=str)

    print(f"Profile JSON saved: {output_path}")
