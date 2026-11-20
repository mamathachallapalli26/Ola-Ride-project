"""
OLA project - STEP 1: DATA PREPROCESSING
=========================================
Reads the raw Excel file, cleans it, creates derived columns, and writes:
    data/ola_clean.csv   -> used by Power BI, Streamlit and the insights script
    data/ola.db          -> SQLite database (table: ola_rides) used by the SQL file
    data/data_quality_report.txt

Usage:
    python 01_data_preprocessing.py --input OLA_DataSet.xlsx
"""
import argparse
import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

OUT_DIR = Path("data")

# ---- 1. COLUMN MAPPING -------------------------------------------------------
# Left = cleaned name used everywhere else. Right = possible raw header names
# (compared after lower-casing and replacing spaces/symbols with "_").
# If your file uses different headers, add them here - nothing else changes.
COLUMN_ALIASES = {
    "booking_id": ["booking_id", "bookingid"],
    "date": ["date"],
    "time": ["time"],
    "booking_status": ["booking_status", "status"],
    "customer_id": ["customer_id", "customerid"],
    "vehicle_type": ["vehicle_type", "vehicletype"],
    "pickup_location": ["pickup_location", "pickup"],
    "drop_location": ["drop_location", "drop"],
    "v_tat": ["v_tat"],
    "c_tat": ["c_tat"],
    "cancel_reason_customer": ["canceled_rides_by_customer", "cancelled_rides_by_customer"],
    "cancel_reason_driver": ["canceled_rides_by_driver", "cancelled_rides_by_driver"],
    "incomplete_ride": ["incomplete_rides", "incomplete_ride"],
    "incomplete_reason": ["incomplete_rides_reason", "incomplete_ride_reason"],
    "booking_value": ["booking_value", "fare"],
    "payment_method": ["payment_method", "payment"],
    "ride_distance": ["ride_distance", "distance"],
    "driver_rating": ["driver_ratings", "driver_rating"],
    "customer_rating": ["customer_rating", "customer_ratings"],
}

# ---- 2. CATEGORY STANDARDISATION --------------------------------------------
# Maps raw spellings -> the names used on your slides.
VEHICLE_MAP = {
    "prime sedan": "Prime Sedan", "premier sedan": "Prime Sedan", "go sedan": "Prime Sedan",
    "prime suv": "Prime SUV", "suv": "Prime SUV", "uberxl": "Prime SUV",
    "prime plus": "Prime Plus",
    "mini": "Mini", "go mini": "Mini",
    "auto": "Auto",
    "bike": "Bike",
    "e-bike": "E-Bike", "ebike": "E-Bike", "e bike": "E-Bike",
}
STATUS_MAP = {
    "success": "Success", "completed": "Success",
    "canceled by customer": "Canceled by Customer", "cancelled by customer": "Canceled by Customer",
    "canceled by driver": "Canceled by Driver", "cancelled by driver": "Canceled by Driver",
    "driver not found": "Driver Not Found", "no driver found": "Driver Not Found",
}


def snake(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={c: snake(c) for c in df.columns})
    lookup = {alias: target for target, aliases in COLUMN_ALIASES.items() for alias in aliases}
    df = df.rename(columns={c: lookup[c] for c in df.columns if c in lookup})
    missing = [c for c in ["booking_id", "date", "booking_status", "vehicle_type"] if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns not found: {missing}. Edit COLUMN_ALIASES. Found: {list(df.columns)}")
    return df


def clean(df: pd.DataFrame, log: list) -> pd.DataFrame:
    log.append(f"Raw rows: {len(df):,} | columns: {df.shape[1]}")
    df = rename_columns(df)

    # Drop image/unnamed columns that are not needed for analysis
    drop_cols = [c for c in df.columns if c.startswith("unnamed") or "image" in c]
    df = df.drop(columns=drop_cols)

    # --- text columns: trim whitespace, collapse spaces
    for col in [c for c in df.columns if pd.api.types.is_object_dtype(df[c]) or pd.api.types.is_string_dtype(df[c])]:
        df[col] = df[col].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
        df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA, "null": pd.NA, "None": pd.NA})

    # --- duplicates
    before = len(df)
    df = df.drop_duplicates(subset="booking_id", keep="first")
    log.append(f"Duplicate Booking_IDs removed: {before - len(df):,}")

    # --- categorical standardisation
    df["vehicle_type"] = df["vehicle_type"].str.lower().map(VEHICLE_MAP).fillna(df["vehicle_type"].str.title())
    df["booking_status"] = df["booking_status"].str.lower().map(STATUS_MAP).fillna(df["booking_status"])
    unknown_v = sorted(set(df["vehicle_type"]) - set(VEHICLE_MAP.values()))
    if unknown_v:
        log.append(f"WARNING unmapped vehicle types (add to VEHICLE_MAP): {unknown_v}")

    # --- date / time
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad_dates = df["date"].isna().sum()
    if "time" in df.columns:
        t = pd.to_datetime(df["time"].astype(str), errors="coerce", format="mixed")
        df["datetime"] = df["date"].dt.normalize() + pd.to_timedelta(
            t.dt.hour.fillna(0) * 3600 + t.dt.minute.fillna(0) * 60 + t.dt.second.fillna(0), unit="s")
    else:
        df["datetime"] = df["date"]
    df = df.dropna(subset=["date"])
    log.append(f"Rows dropped for invalid date: {bad_dates:,}")

    # --- numeric columns
    for col in ["booking_value", "ride_distance", "v_tat", "c_tat", "driver_rating", "customer_rating"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["driver_rating", "customer_rating"]:           # ratings must be 1-5
        if col in df.columns:
            df.loc[~df[col].between(1, 5), col] = np.nan
    for col in ["booking_value", "ride_distance"]:             # no negatives
        if col in df.columns:
            df.loc[df[col] < 0, col] = np.nan

    # --- reason / flag columns: blank means "not applicable", NOT missing data
    for col in ["cancel_reason_customer", "cancel_reason_driver", "incomplete_reason"]:
        if col in df.columns:
            df[col] = df[col].fillna("Not Applicable")
    if "incomplete_ride" in df.columns:
        df["incomplete_ride"] = df["incomplete_ride"].str.lower().isin(["yes", "y", "1", "true"]).astype(int)
    else:
        df["incomplete_ride"] = 0
    if "payment_method" in df.columns:
        df["payment_method"] = df["payment_method"].fillna("Not Applicable")

    # --- derived fields used in SQL / Power BI / Streamlit
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["month_name"] = df["datetime"].dt.strftime("%b")
    df["year_month"] = df["datetime"].dt.strftime("%Y-%m")
    df["weekday"] = df["datetime"].dt.day_name()
    df["hour"] = df["datetime"].dt.hour
    df["time_bucket"] = pd.cut(
        df["hour"], bins=[-1, 5, 11, 16, 20, 23],
        labels=["Night (0-5)", "Morning (6-11)", "Afternoon (12-16)", "Evening (17-20)", "Late Night (21-23)"]
    ).astype(str)
    df["is_success"] = (df["booking_status"] == "Success").astype(int)
    df["is_cancel_customer"] = (df["booking_status"] == "Canceled by Customer").astype(int)
    df["is_cancel_driver"] = (df["booking_status"] == "Canceled by Driver").astype(int)
    df["is_driver_not_found"] = (df["booking_status"] == "Driver Not Found").astype(int)
    df["success_booking_value"] = np.where(df["is_success"] == 1, df["booking_value"], 0.0)

    # Booking value is only meaningful when a ride happened - leave NaN elsewhere, never impute
    log.append("Missing-value summary after cleaning:")
    for col, n in df.isna().sum()[lambda s: s > 0].items():
        log.append(f"   {col}: {n:,} ({n / len(df):.1%})")
    log.append(f"Clean rows: {len(df):,}")
    return df.sort_values("datetime").reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="OLA_DataSet.xlsx")
    ap.add_argument("--sheet", default=0, help="sheet name or index")
    args = ap.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    raw = pd.read_excel(args.input, sheet_name=args.sheet)
    log: list = []
    df = clean(raw, log)

    df.to_csv(OUT_DIR / "ola_clean.csv", index=False)
    with sqlite3.connect(OUT_DIR / "ola.db") as con:
        df.assign(date=df["date"].dt.strftime("%Y-%m-%d"),
                  datetime=df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
                  ).to_sql("ola_rides", con, if_exists="replace", index=False)
    (OUT_DIR / "data_quality_report.txt").write_text("\n".join(log), encoding="utf-8")
    print("\n".join(log))
    print(f"\nSaved: {OUT_DIR/'ola_clean.csv'}, {OUT_DIR/'ola.db'}")


if __name__ == "__main__":
    main()
