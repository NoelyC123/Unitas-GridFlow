from __future__ import annotations

import pandas as pd
from pyproj import Transformer

# Detection ranges derived from official OSi/EPSG specs.
# ITM (EPSG:2157): false E=600000 / N=750000 — Ireland practical extent
# TM65 (EPSG:29900): false E=200000 / N=250000 — old Irish National Grid
_ITM_E = (450_000.0, 810_000.0)
_ITM_N = (490_000.0, 990_000.0)
_TM65_E = (0.0, 360_000.0)
_TM65_N = (0.0, 490_000.0)

# Column aliases specific to raw GPS controller exports (Trimble/Leica etc.)
_CONTROLLER_ALIASES: dict[str, list[str]] = {
    "pole_id": ["point", "pt", "pnt", "point_no", "no", "name", "number"],
    "easting": ["e", "east", "grid_e", "grid_east", "x"],
    "northing": ["n", "north", "grid_n", "grid_north", "y"],
    "height": ["h", "elev", "elevation", "z"],
    "structure_type": ["code", "feature_code", "feat_code", "fc"],
    "location": ["desc", "description", "notes", "note", "comment", "remarks"],
}

# Column names that strongly indicate a raw controller export
_CONTROLLER_INDICATOR_COLS: frozenset[str] = frozenset(
    {
        "point",
        "pt",
        "pnt",
        "code",
        "feat_code",
        "feature_code",
        "grid_e",
        "grid_n",
        "elev",
        "elevation",
    }
)

_KEY_SCHEMA_FIELDS = [
    "pole_id",
    "easting",
    "northing",
    "lat",
    "lon",
    "height",
    "structure_type",
    "material",
    "location",
]


def detect_grid_crs(easting: float, northing: float) -> str:
    """Return the most likely EPSG CRS code for a representative easting/northing pair."""
    if _ITM_E[0] <= easting <= _ITM_E[1] and _ITM_N[0] <= northing <= _ITM_N[1]:
        return "EPSG:2157"
    if _TM65_E[0] <= easting <= _TM65_E[1] and _TM65_N[0] <= northing <= _TM65_N[1]:
        return "EPSG:29900"
    return "EPSG:27700"


def convert_grid_to_wgs84(df: pd.DataFrame) -> pd.DataFrame:
    """
    If df has easting/northing but no lat/lon, detect CRS from the first valid
    coordinate pair and reproject the full column to WGS84 lat/lon.
    Adds a '_grid_crs' audit column recording which CRS was used.
    Returns df unchanged if lat/lon already present or grid coords are absent.
    """
    has_latlon = "lat" in df.columns and df["lat"].notna().any()
    has_grid = "easting" in df.columns and "northing" in df.columns

    if has_latlon or not has_grid:
        return df

    valid = df["easting"].notna() & df["northing"].notna()
    if not valid.any():
        return df

    sample_e = float(df.loc[valid, "easting"].iloc[0])
    sample_n = float(df.loc[valid, "northing"].iloc[0])
    epsg = detect_grid_crs(sample_e, sample_n)

    transformer = Transformer.from_crs(epsg, "EPSG:4326", always_xy=True)
    lons, lats = transformer.transform(
        df.loc[valid, "easting"].to_numpy(dtype=float),
        df.loc[valid, "northing"].to_numpy(dtype=float),
    )

    df = df.copy()
    df.loc[valid, "lon"] = lons
    df.loc[valid, "lat"] = lats
    df["_grid_crs"] = epsg

    return df


def is_controller_csv(df: pd.DataFrame) -> bool:
    """Return True if df looks like a raw GPS controller export."""
    normalised = {col.strip().lower().replace(" ", "_") for col in df.columns}
    return bool(normalised & _CONTROLLER_INDICATOR_COLS)


def _resolve_controller_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map raw controller column names to internal schema names in-place."""
    df = df.copy()
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    for target, candidates in _CONTROLLER_ALIASES.items():
        if target not in df.columns:
            for cand in candidates:
                if cand in df.columns:
                    df.rename(columns={cand: target}, inplace=True)
                    break

    return df


def parse_controller_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise a raw GPS controller CSV into the internal schema and convert
    grid coordinates to WGS84 lat/lon if no lat/lon columns are present.
    Generates sequential pole_id values when none can be inferred.
    """
    df = _resolve_controller_columns(df)

    for col in ("easting", "northing", "height"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = convert_grid_to_wgs84(df)

    if "pole_id" not in df.columns or df["pole_id"].isna().all():
        df["pole_id"] = [f"P-{i + 1:04d}" for i in range(len(df))]

    return df


def build_completeness_summary(df: pd.DataFrame) -> dict:
    """
    Return a completeness/capture summary for a parsed survey dataframe.
    Reports per-field coverage and overall position data status.
    """
    total = len(df)
    if total == 0:
        return {"total_records": 0, "fields": {}, "position_status": "no_data"}

    fields: dict[str, dict] = {}
    for field in _KEY_SCHEMA_FIELDS:
        if field in df.columns:
            present = int(df[field].notna().sum())
            fields[field] = {
                "present": present,
                "missing": total - present,
                "coverage_pct": round(100 * present / total, 1),
            }
        else:
            fields[field] = {
                "present": 0,
                "missing": total,
                "coverage_pct": 0.0,
            }

    has_latlon = (
        "lat" in df.columns
        and df["lat"].notna().any()
        and "lon" in df.columns
        and df["lon"].notna().any()
    )
    has_grid = (
        "easting" in df.columns
        and df["easting"].notna().any()
        and "northing" in df.columns
        and df["northing"].notna().any()
    )

    if has_latlon and has_grid:
        position_status = "latlon_and_grid"
    elif has_latlon:
        position_status = "latlon_only"
    elif has_grid:
        position_status = "grid_only"
    else:
        position_status = "no_position"

    crs_col = df.get("_grid_crs", pd.Series(dtype=str)).dropna()
    grid_crs_detected = str(crs_col.iloc[0]) if len(crs_col) else None

    return {
        "total_records": total,
        "fields": fields,
        "position_status": position_status,
        "grid_crs_detected": grid_crs_detected,
    }
