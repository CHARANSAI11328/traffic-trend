from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import logging
from backend.app.core.helpers import normalize_column_name, detect_column_mappings

logger = logging.getLogger(__name__)

@dataclass
class CleaningOptions:
    """Configurable data cleaning parameters."""
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
        if options is None:
            options = CleaningOptions()

        orig_count = len(df)
        cleaned = df.copy()
        mods = []

        logger.info(f"Initiating data cleaning on {orig_count} records")

        # 1. Deduplication
        dups_removed = 0
        if options.drop_duplicates:
            before_dup = len(cleaned)
            cleaned = cleaned.drop_duplicates()
            dups_removed = before_dup - len(cleaned)
            if dups_removed > 0:
                mods.append(f"Removed {dups_removed} exact duplicate records")

        # 2. Map Columns if raw
        mappings = detect_column_mappings(list(cleaned.columns))
        rename_dict = {orig: canon for canon, orig in mappings.items() if orig in cleaned.columns}
        if rename_dict:
            cleaned = cleaned.rename(columns=rename_dict)
            mods.append(f"Mapped {len(rename_dict)} columns to canonical schema")

        # 3. Date Normalization
        invalid_dates_dropped = 0
        if "accident_date" in cleaned.columns:
            date_series = pd.to_datetime(cleaned["accident_date"], errors="coerce")
            invalid_mask = date_series.isna()
            invalid_dates_dropped = int(invalid_mask.sum())
            if invalid_dates_dropped > 0:
                if options.handle_missing_dates == "drop":
                    cleaned = cleaned[~invalid_mask].copy()
                    date_series = date_series[~invalid_mask]
                    mods.append(f"Dropped {invalid_dates_dropped} records with unparseable accident dates")
            cleaned["accident_date"] = date_series.dt.strftime("%Y-%m-%d")
            
            # Populate year, month, day_of_week if missing
            if "year" not in cleaned.columns or cleaned["year"].isna().all():
                cleaned["year"] = date_series.dt.year
            if "month" not in cleaned.columns or cleaned["month"].isna().all():
                cleaned["month"] = date_series.dt.strftime("%B")
            if "day_of_week" not in cleaned.columns or cleaned["day_of_week"].isna().all():
                cleaned["day_of_week"] = date_series.dt.strftime("%A")

        # 4. Casualties & Severity Auditing
        missing_imputed_count = 0
        negative_casualties_corrected = 0

        for col in ["fatalities_count", "injured_count", "vehicles_involved_count"]:
            if col in cleaned.columns:
                num_series = pd.to_numeric(cleaned[col], errors="coerce")
                nan_count = int(num_series.isna().sum())
                if nan_count > 0:
                    num_series = num_series.fillna(0 if "count" in col and col != "vehicles_involved_count" else 1)
                    missing_imputed_count += nan_count
                    mods.append(f"Imputed {nan_count} missing values in {col}")
                
                if options.enforce_non_negative_casualties:
                    neg_mask = num_series < 0
                    neg_count = int(neg_mask.sum())
                    if neg_count > 0:
                        num_series = num_series.clip(lower=0)
                        negative_casualties_corrected += neg_count
                        mods.append(f"Corrected {neg_count} negative entries in {col} to 0")
                cleaned[col] = num_series.astype(int)

        # 5. Coordinate Sanitization
        invalid_coordinates_nulled = 0
        if options.validate_coordinates:
            for coord_col, (min_val, max_val) in [("latitude", (-90.0, 90.0)), ("longitude", (-180.0, 180.0))]:
                if coord_col in cleaned.columns:
                    coord_series = pd.to_numeric(cleaned[coord_col], errors="coerce")
                    invalid_mask = coord_series.isna() | (coord_series < min_val) | (coord_series > max_val)
                    inv_count = int(invalid_mask.sum())
                    if inv_count > 0:
                        cleaned.loc[invalid_mask, coord_col] = np.nan
                        invalid_coordinates_nulled += inv_count
                        mods.append(f"Nulled {inv_count} invalid values in {coord_col} outside [{min_val}, {max_val}]")
                    cleaned[coord_col] = coord_series

        # 6. Categorical Standardisation
        if options.impute_missing_categoricals:
            categorical_cols = [
                "state", "district", "location_type", "road_type", "road_condition",
                "weather", "light_condition", "accident_severity", "collision_type",
                "primary_vehicle_type", "contributing_factor"
            ]
            for cat_col in categorical_cols:
                if cat_col in cleaned.columns:
                    missing_mask = cleaned[cat_col].isna() | (cleaned[cat_col].astype(str).str.strip() == "")
                    mis_cnt = int(missing_mask.sum())
                    if mis_cnt > 0:
                        cleaned.loc[missing_mask, cat_col] = options.categorical_fill_value
                        missing_imputed_count += mis_cnt
                        mods.append(f"Imputed {mis_cnt} missing entries in '{cat_col}' as '{options.categorical_fill_value}'")

        final_count = len(cleaned)
        summary = CleaningSummary(
            original_records=orig_count,
            retained_records=final_count,
            duplicates_removed=dups_removed,
            missing_imputed_count=missing_imputed_count,
            invalid_dates_dropped=invalid_dates_dropped,
            invalid_coordinates_nulled=invalid_coordinates_nulled,
            negative_casualties_corrected=negative_casualties_corrected,
            final_records=final_count,
            modifications_log=mods
        )

        return cleaned, summary
