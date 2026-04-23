from __future__ import annotations

import csv
from pathlib import Path

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

# Feature codes used to classify record roles during intake.
# Keep in sync with qa_engine._CONTEXT_FEATURE_CODES and _STRUCTURAL_FEATURE_CODES.
_STRUCTURAL_CODES: frozenset[str] = frozenset(
    {
        "Pol",
        "pol",
        "POL",
        "Angle",
        "angle",
        "ANGLE",
        "EXpole",
        "expole",
        "EXPOLE",
        "Terminal",
        "terminal",
        "TERMINAL",
        "Stay pole",
        "Service pole",
        "Pole",
        "pole",
        "POLE",
        "Wood Pole",
        "Steel Pole",
        "Concrete Pole",
        "Composite Pole",
    }
)

_CONTEXT_CODES: frozenset[str] = frozenset(
    {
        "Hedge",
        "hedge",
        "HEDGE",
        "Tree",
        "tree",
        "TREE",
        "Wall",
        "wall",
        "WALL",
        "Fence",
        "fence",
        "FENCE",
        "Post",
        "post",
        "POST",
        "Gate",
        "gate",
        "GATE",
        "Track",
        "track",
        "TRACK",
        "Stream",
        "stream",
        "STREAM",
    }
)


def _classify_role(row: "pd.Series") -> str:
    """Return 'structural', 'context', or 'anchor' for a single survey row."""
    st = row.get("structure_type")
    if st is None or (isinstance(st, str) and st.strip() == ""):
        # No feature code: distinguish anchor reference points from uncoded survey rows.
        # Pure-numeric pole IDs (1, 2, 20, ...) are survey points — treat conservatively.
        # Non-numeric IDs without a feature code are anchor/reference markers.
        pole_id = str(row.get("pole_id") or "")
        if pole_id.replace("-", "").replace(".", "").isdigit():
            return "structural"
        return "anchor"
    st_str = str(st).strip()
    if st_str in _STRUCTURAL_CODES:
        return "structural"
    if st_str in _CONTEXT_CODES:
        return "context"
    return "structural"  # unknown feature code → conservative


def classify_record_roles(df: pd.DataFrame) -> pd.DataFrame:
    """Add a _record_role column ('structural', 'context', 'anchor') to df.

    The column gates structural QA rules and powers the file composition
    summary shown in the map side panel and PDF report.
    """
    df = df.copy()
    df["_record_role"] = df.apply(_classify_role, axis=1)
    return df


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


def is_raw_controller_dump(first_line: str) -> bool:
    """
    Return True if first_line matches the GNSS controller metadata header format.
    Detects: Job:<name>,Version:<n>,Units:<unit>
    This format cannot be read by pd.read_csv() with default settings because
    the metadata row is treated as the column header, breaking all field detection.
    """
    stripped = first_line.strip()
    return stripped.startswith("Job:") and "Version:" in stripped and "Units:" in stripped


def parse_raw_controller_dump(path: Path | str) -> pd.DataFrame:
    """
    Parse a raw GNSS controller CSV dump where row 0 is a metadata header
    (Job:X,Version:Y,Units:Z) rather than column names.

    Row layout (after skipping header and base station):
      Col 0  → pole_id (survey point number)
      Col 1  → easting
      Col 2  → northing
      Col 3  → GPS instrument elevation — NOT pole height; intentionally omitted
      Col 4  → structure_type (feature code: Angle, Pol, Hedge, EXpole, ...)
      Col 5+ → alternating inline attribute pairs: FeatureCode:ATTR_TYPE, value
                Recognised ATTR_TYPEs: HEIGHT → height, REMARK → location

    GPS elevation is intentionally not mapped to 'height' because it records
    terrain/instrument elevation, not declared pole height. This ensures
    build_completeness_summary correctly reports partial height coverage
    (only rows with an explicit HEIGHT attribute have height data).

    Uses Python's csv module rather than pd.read_csv because the raw dump
    has variable column counts per row (metadata row has 3 fields; data rows
    can have 20+), which the pandas C parser cannot handle without errors.
    """
    records: list[dict] = []

    with open(path, encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.reader(fh)
        for raw_row in reader:
            values = [v.strip() for v in raw_row if v.strip()]

            if not values:
                continue

            first = values[0]

            # Skip metadata header (Job:...) and base station rows (PRS...)
            if first.startswith("Job:") or first.upper().startswith("PRS"):
                continue

            if len(values) < 3:
                continue

            point_num = first
            try:
                easting = float(values[1])
                northing = float(values[2])
            except ValueError:
                continue

            # Feature code at col 4 → structure_type
            feature_code = values[4] if len(values) > 4 else None

            # Parse inline attribute pairs from col 5 onwards
            height: float | None = None
            remark: str | None = None

            idx = 5
            while idx + 1 < len(values):
                attr_key = values[idx]
                attr_val = values[idx + 1]
                idx += 2

                if ":" not in attr_key:
                    continue

                attr_type = attr_key.split(":", 1)[1].upper()

                if attr_type == "HEIGHT" and attr_val:
                    try:
                        height = float(attr_val)
                    except ValueError:
                        pass
                elif attr_type == "REMARK" and attr_val:
                    remark = attr_val or None

            records.append(
                {
                    "pole_id": point_num,
                    "easting": easting,
                    "northing": northing,
                    "height": height,
                    "structure_type": feature_code,
                    "location": remark,
                }
            )

    if not records:
        return pd.DataFrame(
            columns=["pole_id", "easting", "northing", "height", "structure_type", "location"]
        )

    df = pd.DataFrame(records)
    for col in ("easting", "northing", "height"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


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
    Reports per-field coverage, overall position status, and record-role breakdown
    when _record_role is present.
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

    result: dict = {
        "total_records": total,
        "fields": fields,
        "position_status": position_status,
        "grid_crs_detected": grid_crs_detected,
    }

    # Surface unique feature/structure codes present in the digital file.
    if "structure_type" in df.columns:
        unique_codes = sorted(
            str(v) for v in df["structure_type"].dropna().unique().tolist() if str(v).strip()
        )
        if unique_codes:
            result["feature_codes_found"] = unique_codes

    # Role-based breakdown and structural-specific field coverage.
    if "_record_role" in df.columns:
        role_counts = df["_record_role"].value_counts().to_dict()
        structural_count = int(role_counts.get("structural", 0))
        context_count = int(role_counts.get("context", 0))
        anchor_count = int(role_counts.get("anchor", 0))
        result["structural_count"] = structural_count
        result["context_count"] = context_count
        result["anchor_count"] = anchor_count

        # Per-field coverage on structural records only — avoids context features
        # (Gate height 1.2m, Fence height 1.8m) polluting the structural stats.
        if structural_count > 0:
            s_df = df[df["_record_role"] == "structural"]
            structural_fields: dict[str, dict] = {}
            for fld in ("height", "material", "location"):
                if fld in s_df.columns:
                    present = int(s_df[fld].notna().sum())
                    structural_fields[fld] = {
                        "present": present,
                        "missing": structural_count - present,
                        "coverage_pct": round(100 * present / structural_count, 1),
                    }
            if structural_fields:
                result["structural_fields"] = structural_fields

    return result


def _coverage_rating(pct: float) -> str:
    if pct > 70:
        return "Strong"
    if pct > 0:
        return "Partial"
    return "Missing"


def _position_pct(fields: dict) -> float:
    """
    Position & Identity coverage: best coordinate field (lat preferred, else easting)
    averaged with pole_id and structure_type coverage.
    """
    lat_pct = fields.get("lat", {}).get("coverage_pct", 0.0)
    easting_pct = fields.get("easting", {}).get("coverage_pct", 0.0)
    coord_pct = max(lat_pct, easting_pct)
    pole_id_pct = fields.get("pole_id", {}).get("coverage_pct", 0.0)
    structure_pct = fields.get("structure_type", {}).get("coverage_pct", 0.0)
    return round((coord_pct + pole_id_pct + structure_pct) / 3, 1)


def build_design_readiness(completeness: dict) -> dict:
    """
    Derive a design readiness verdict and per-category coverage ratings from
    existing completeness data. No new inputs required.

    Uses structural-specific field coverage (structural_fields) when available
    so that context-feature heights (Gate=1.2m, Fence=1.8m) do not distort the
    assessment of whether structural pole data is complete.

    Returns:
        verdict: NOT READY / PARTIALLY READY / LIKELY READY
        reasons: list explaining what this file does and does not support
        what_this_supports: positive list of what the file enables
        coverage: category → Strong / Partial / Missing
    """
    fields = completeness.get("fields") or {}
    # Use structural-specific coverage where available; fall back to all-record fields.
    s_fields = completeness.get("structural_fields") or fields

    pos_pct = _position_pct(fields)
    height_pct = s_fields.get("height", {}).get("coverage_pct", 0.0)
    material_pct = s_fields.get("material", {}).get("coverage_pct", 0.0)
    structural_pct = round((height_pct + material_pct) / 2, 1)

    structural_count = completeness.get("structural_count")
    total = completeness.get("total_records", 0)
    # Descriptor used in reason text: prefer structural count if available.
    rec_noun = (
        f"{structural_count} structural record{'s' if structural_count != 1 else ''}"
        if structural_count is not None
        else f"{total} record{'s' if total != 1 else ''}"
    )

    coverage: dict[str, str] = {
        "Position & Identity": _coverage_rating(pos_pct),
        "Structural Data": _coverage_rating(structural_pct),
        "Electrical Configuration": "Missing",
        "Stability & Safety": "Missing",
        "Clearances": "Missing",
        "Environment & Access": "Missing",
    }

    position_rating = coverage["Position & Identity"]
    structural_rating = coverage["Structural Data"]

    reasons: list[str] = []
    what_supports: list[str] = []

    st_pct = fields.get("structure_type", {}).get("coverage_pct", 0.0)
    context_count_n = completeness.get("context_count") or 0

    if position_rating == "Missing":
        reasons.append(f"{rec_noun} cannot be located — position data absent from digital file")
    elif position_rating == "Partial":
        reasons.append(
            f"not all {rec_noun} can be reliably located — position data incomplete in digital file"
        )
    else:
        what_supports.append(f"locating {rec_noun} on the network")

    if st_pct > 70:
        what_supports.append("identifying pole types and network roles along the route")

    if context_count_n > 0:
        noun = "feature" if context_count_n == 1 else "features"
        what_supports.append(
            f"locating {context_count_n} environmental and crossing {noun} along the route"
        )

    if height_pct == 0.0 and material_pct == 0.0:
        reasons.append(
            "height and material absent from digital file"
            " — clearance, sag, and structural checks cannot be run"
        )
    else:
        if height_pct >= 70.0:
            h_present = s_fields.get("height", {}).get("present", 0)
            what_supports.append(
                f"height-based clearance checks for {h_present} of {structural_count or total}"
                f" structural records"
            )
        else:
            h_present = s_fields.get("height", {}).get("present", 0)
            s_total = structural_count or total
            label = (
                "not captured in digital file"
                if height_pct == 0.0
                else f"recorded for {h_present} of {s_total} structural records"
            )
            reasons.append(f"height {label} — clearance and sag design checks not fully supported")
        if material_pct < 70.0:
            label = (
                "not captured in digital file"
                if material_pct == 0.0
                else f"{material_pct}% of structural records"
            )
            reasons.append(
                f"material {label}"
                f" — structural loading and suitability require field notes or plan markups"
            )

    reasons.append(
        "stays, clearances, conductor scope, and loading data are not in the digital"
        " export — field notes and plans required for design"
    )

    if material_pct == 0.0:
        reasons.insert(
            0,
            "This file cannot support full design — critical design data missing",
        )

    if position_rating == "Missing":
        verdict = "NOT READY"
    elif position_rating == "Strong" and structural_rating == "Strong":
        verdict = "LIKELY READY"
    else:
        verdict = "PARTIALLY READY"

    result: dict = {
        "verdict": verdict,
        "reasons": reasons,
        "coverage": coverage,
    }
    if what_supports:
        result["what_this_supports"] = what_supports
    return result
