"""
Data Loader Module for TRAFFIC TREND Platform
Supports CSV, Excel (XLSX, XLS), and Parquet with automated schema mapping.
"""
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from src.utils.helpers import compute_checksum, detect_column_mappings, normalize_column_name
from src.utils.configuration import CONFIG
from src.monitoring.logger import logger

class DataLoader:
    """Robust file ingestion engine handling diverse encodings, formats and schemas."""

    SUPPORTED_EXTENSIONS = [".csv", ".xlsx", ".xls", ".parquet"]

    @classmethod
    def load_file(
        cls,
        file_path_or_buffer: Union[str, Path, Any],
        filename: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Loads dataset from disk path or uploaded file buffer.
        Returns (DataFrame, metadata_dict).
        """
        ext = ""
        name = "unnamed_dataset"
        
        if isinstance(file_path_or_buffer, (str, Path)):
            path = Path(file_path_or_buffer)
            ext = path.suffix.lower()
            name = path.name
            checksum = compute_checksum(path)
            size_bytes = path.stat().st_size
        else:
            name = getattr(file_path_or_buffer, "name", filename or "uploaded_dataset")
            ext = Path(name).suffix.lower()
            size_bytes = getattr(file_path_or_buffer, "size", 0)
            checksum = compute_checksum(file_path_or_buffer)

        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format '{ext}'. Must be one of: {cls.SUPPORTED_EXTENSIONS}")

        logger.info(f"Loading file: {name} (Format: {ext}, Size: {size_bytes} bytes)")

        df = cls._read_raw_dataframe(file_path_or_buffer, ext)
        
        # Discover and document schema
        detected_mappings = detect_column_mappings(list(df.columns))
        
        metadata = {
            "dataset_name": name,
            "file_type": ext.lstrip(".").upper(),
            "file_size_bytes": size_bytes,
            "checksum_sha256": checksum,
            "original_columns": list(df.columns),
            "record_count": len(df),
            "column_count": len(df.columns),
            "detected_mappings": detected_mappings
        }

        return df, metadata

    @classmethod
    def _read_raw_dataframe(cls, source: Any, ext: str) -> pd.DataFrame:
        """Reads DataFrame using suitable engine and fallback encodings."""
        if ext == ".csv":
            encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252", "iso-8859-1"]
            last_err = None
            for enc in encodings:
                try:
                    if hasattr(source, "seek"):
                        source.seek(0)
                    df = pd.read_csv(source, encoding=enc, low_memory=False)
                    logger.debug(f"Successfully loaded CSV with encoding: {enc}")
                    return df
                except Exception as e:
                    last_err = e
                    continue
            raise ValueError(f"Failed to decode CSV across common encodings: {last_err}")

        elif ext in [".xlsx", ".xls"]:
            if hasattr(source, "seek"):
                source.seek(0)
            return pd.read_excel(source, engine="openpyxl" if ext == ".xlsx" else None)

        elif ext == ".parquet":
            if hasattr(source, "seek"):
                source.seek(0)
            return pd.read_parquet(source)

        raise ValueError(f"Unsupported extension: {ext}")

    @classmethod
    def apply_canonical_mapping(cls, df: pd.DataFrame, mappings: Dict[str, str]) -> pd.DataFrame:
        """
        Projects arbitrary source columns into canonical schema while preserving original columns.
        """
        mapped_df = df.copy()
        
        # Rename identified columns to canonical names
        rename_dict = {orig: canon for canon, orig in mappings.items() if orig in mapped_df.columns}
        mapped_df.rename(columns=rename_dict, inplace=True)
        
        # Normalize canonical column names
        cols_present = mapped_df.columns.tolist()
        
        return mapped_df

