from pathlib import Path
from typing import Tuple, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
import logging
from backend.app.core.helpers import compute_checksum, detect_column_mappings, normalize_column_name

logger = logging.getLogger(__name__)

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
            for enc in encodings:
                try:
                    if hasattr(source, "seek"):
                        source.seek(0)
                    return pd.read_csv(source, encoding=enc, low_memory=False)
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    if enc == encodings[-1]:
                        raise e
            raise ValueError("Failed to decode CSV with supported encodings.")
        
        elif ext in [".xlsx", ".xls"]:
            if hasattr(source, "seek"):
                source.seek(0)
            return pd.read_excel(source, engine="openpyxl")
        
        elif ext == ".parquet":
            if hasattr(source, "seek"):
                source.seek(0)
            return pd.read_parquet(source)
            
        raise ValueError(f"Unsupported extension: {ext}")
