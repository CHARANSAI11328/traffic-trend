"""
Configurable Data Cleaning Engine for TRAFFIC TREND Platform
Preserves raw records, tracks provenance, and audits all transformations.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from src.monitoring.logger import logger

@dataclass
class CleaningOptions:
    """Configurable data cleaning parameters selected by analyst."""
    drop_duplicates: bool = True
    dedup_subset: Optional[List[str]] = None
    handle_missing_dates: str = "drop"  # "drop" or "coerce"
    handle_missing_severity: str = "impute_unknown"  # "drop" or "impute_unknown"
    handle_missing_casualties: str = "impute_zero"  # "drop" or "impute_zero"
    impute_missing_categoricals: bool = True
    categorical_fill_value: str = "Unknown"
    validate_coordinates: bool = True
    enforce_non_negative_casualties: bool = True

@dataclass
class CleaningSummary:
    """Audit summary of cleaning operations applied."""
    original_records: int
    retained_records: int
    duplicates_removed: int
    missing_imputed_count: int
    invalid_dates_dropped: int
    invalid_coordinates_nulled: int
    negative_casualties_corrected: int
    final_records: int
    modifications_log: List[str] = field(default_factory=list)


class DataCleaner:
    """Performs defensive, auditable cleaning on accident datasets."""

    @classmethod
    def clean(
        cls,
        df: pd.DataFrame,
        options: Optional[CleaningOptions] = None
    ) -> Tuple[pd.DataFrame, CleaningSummary]:
        """
        Executes pipeline: Deduplication -> Date/Time Normalization -> 
        Casualty Auditing -> Coordinate Sanitization -> Categorical Cleaning.
        """
        if options is None:
            options = CleaningOptions()

        orig_count = len(df)
        cleaned = df.copy()
        mods = []

        logger.info(f"Initiating data cleaning on {orig_count} records with options: {options}")

        # 1. Deduplication
        dups_removed = 0
        if options.drop_duplicates:
            subset = options.dedup_subset
            if subset:
                valid_subset = [c for c in subset if c in cleaned.columns]
                if valid_subset:
                    before_dup = len(cleaned)
                    cleaned = cleaned.drop_duplicates(subset=valid_subset)
                    dups_removed = before_dup - len(cleaned)
                    if dups_removed > 0:
                        mods.append(f"Removed {dups_removed} duplicates based on key subset: {valid_subset}")
            else:
                before_dup = len(cleaned)
                cleaned = cleaned.drop_duplicates()
                dups_removed = before_dup - len(cleaned)
                if dups_removed > 0:
                    mods.append(f"Removed {dups_removed} exact duplicate records")

        # 2. Date and Time Normalization
        invalid_dates_dropped = 0
        date_col = next((c for c in ["accident_date", "date"] if c in cleaned.columns), None)
        if date_col:
            # Parse dates
            raw_dates = pd.to_datetime(cleaned[date_col], errors="coerce")
            invalid_mask = raw_dates.isna()
            invalid_count = invalid_mask.sum()

            if invalid_count > 0:
                if options.handle_missing_dates == "drop":
                    cleaned = cleaned.loc[~invalid_mask].copy()
                    raw_dates = raw_dates.loc[~invalid_mask]
                    invalid_dates_dropped = int(invalid_count)
                    mods.append(f"Excluded {invalid_count} records due to unparseable or missing date values")
                else:
                    mods.append(f"Coerced {invalid_count} unparseable dates to NaT")

            cleaned[date_col] = raw_dates

            # Enrich temporal dimensions if missing
            if "year" not in cleaned.columns:
                cleaned["year"] = cleaned[date_col].dt.year
            else:
                cleaned["year"] = cleaned["year"].fillna(cleaned[date_col].dt.year)

            if "month" not in cleaned.columns:
                cleaned["month"] = cleaned[date_col].dt.month_name()
            else:
                cleaned["month"] = cleaned["month"].fillna(cleaned[date_col].dt.month_name())

            if "day_of_week" not in cleaned.columns:
                cleaned["day_of_week"] = cleaned[date_col].dt.day_name()
            else:
                cleaned["day_of_week"] = cleaned["day_of_week"].fillna(cleaned[date_col].dt.day_name())

        # Time and Hour Parsing
        time_col = next((c for c in ["accident_time", "time"] if c in cleaned.columns), None)
        if time_col and "hour_of_day" not in cleaned.columns:
            try:
                parsed_time = pd.to_datetime(cleaned[time_col].astype(str), format="%H:%M:%S", errors="coerce")
                cleaned["hour_of_day"] = parsed_time.dt.hour
            except Exception:
                pass

        # 3. Casualty Figures Audit (Fatalities, Injuries, Vehicles)
        negative_casualties = 0
        imputed_casualties = 0
        casualty_cols = ["fatalities_count", "injured_count", "vehicles_involved_count"]
        for c_col in casualty_cols:
            if c_col in cleaned.columns:
                # Force numeric
                cleaned[c_col] = pd.to_numeric(cleaned[c_col], errors="coerce")
                
                # Handle nulls
                c_nulls = cleaned[c_col].isna().sum()
                if c_nulls > 0:
                    if options.handle_missing_casualties == "impute_zero":
                        cleaned[c_col] = cleaned[c_col].fillna(0)
                        imputed_casualties += int(c_nulls)
                        mods.append(f"Imputed {c_nulls} missing values in '{c_col}' with 0")
                    elif options.handle_missing_casualties == "drop":
                        cleaned = cleaned.dropna(subset=[c_col])
                        mods.append(f"Dropped {c_nulls} records with null in '{c_col}'")

                # Sanity: negative values
                if options.enforce_non_negative_casualties:
                    neg_mask = cleaned[c_col] < 0
                    neg_count = neg_mask.sum()
                    if neg_count > 0:
                        cleaned.loc[neg_mask, c_col] = 0
                        negative_casualties += int(neg_count)
                        mods.append(f"Clamped {neg_count} negative entries in '{c_col}' to 0")

                cleaned[c_col] = cleaned[c_col].astype(int, errors="ignore")

        # 4. Coordinate Sanitization
        invalid_coords = 0
        if options.validate_coordinates:
            if "latitude" in cleaned.columns:
                cleaned["latitude"] = pd.to_numeric(cleaned["latitude"], errors="coerce")
                bad_lat = (~cleaned["latitude"].isna()) & ((cleaned["latitude"] < -90.0) | (cleaned["latitude"] > 90.0))
                if bad_lat.sum() > 0:
                    invalid_coords += int(bad_lat.sum())
                    cleaned.loc[bad_lat, "latitude"] = np.nan
                    mods.append(f"Nulled {bad_lat.sum()} out-of-range latitude values (expected [-90, +90])")

            if "longitude" in cleaned.columns:
                cleaned["longitude"] = pd.to_numeric(cleaned["longitude"], errors="coerce")
                bad_lon = (~cleaned["longitude"].isna()) & ((cleaned["longitude"] < -180.0) | (cleaned["longitude"] > 180.0))
                if bad_lon.sum() > 0:
                    invalid_coords += int(bad_lon.sum())
                    cleaned.loc[bad_lon, "longitude"] = np.nan
                    mods.append(f"Nulled {bad_lon.sum()} out-of-range longitude values (expected [-180, +180])")

        # 5. Categorical Sanitization & Imputation
        categoricals = [
            "accident_severity", "state", "district", "road_type", 
            "road_condition", "weather", "light_condition", 
            "collision_type", "primary_vehicle_type", "contributing_factor", "location_type"
        ]
        for cat in categoricals:
            if cat in cleaned.columns:
                cleaned[cat] = cleaned[cat].astype(str).str.strip()
                cleaned[cat] = cleaned[cat].replace({"nan": np.nan, "None": np.nan, "": np.nan})
                
                cat_nulls = cleaned[cat].isna().sum()
                if cat_nulls > 0 and options.impute_missing_categoricals:
                    cleaned[cat] = cleaned[cat].fillna(options.categorical_fill_value)
                    mods.append(f"Imputed {cat_nulls} missing entries in '{cat}' with '{options.categorical_fill_value}'")

        # 6. Logical Severity Alignment
        if "accident_severity" in cleaned.columns and "fatalities_count" in cleaned.columns:
            # If fatalities > 0 and severity says minor or unknown, upgrade to Fatal for consistency
            mismatch = (cleaned["fatalities_count"] > 0) & (cleaned["accident_severity"].str.lower().isin(["minor", "unknown", "property damage only"]))
            if mismatch.sum() > 0:
                cleaned.loc[mismatch, "accident_severity"] = "Fatal"
                mods.append(f"Aligned {mismatch.sum()} records with fatal casualties to 'Fatal' severity class")

        final_count = len(cleaned)
        summary = CleaningSummary(
            original_records=orig_count,
            retained_records=final_count,
            duplicates_removed=dups_removed,
            missing_imputed_count=imputed_casualties,
            invalid_dates_dropped=invalid_dates_dropped,
            invalid_coordinates_nulled=invalid_coords,
            negative_casualties_corrected=negative_casualties,
            final_records=final_count,
            modifications_log=mods
        )

        logger.info(f"Cleaning completed: {orig_count} -> {final_count} records retained ({dups_removed} duplicates removed).")
        return cleaned, summary

