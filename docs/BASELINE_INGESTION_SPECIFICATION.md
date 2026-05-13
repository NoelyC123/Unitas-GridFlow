# Stage 4C.1 Baseline Ingestion Specification

**Version**: 1.0
**Date**: 2026-05-13
**Status**: Complete
**Authority**: Stage 4C Implementation Roadmap

## Executive Summary

The Stage 4C.1 Baseline Ingestion Engine is a production-grade system that ingests, validates, and normalizes overhead line baseline data from DNO GIS systems (ENWL, NGED, SPEN, SSEN, UKPN, NPG) and Trimble survey exports.

It provides the critical data foundation for Stage 4C (Structured Field-to-Baseline Capture) by:
1. Parsing diverse CSV formats reliably
2. Validating data quality and completeness
3. Normalizing coordinates and identifiers
4. Reconstructing missing route/sequence information
5. Generating standardized JSON output suitable for design integration

## Objectives

### Primary

1. **Reliability**: Parse real-world DNO data without failure
2. **Completeness**: Preserve all baseline information in standardized form
3. **Validation**: Detect and report data quality issues
4. **Performance**: Handle 10,000+ pole datasets efficiently
5. **Maintainability**: Production-grade code with ≥80% test coverage

### Secondary

1. **Extensibility**: Support additional DNO formats without core changes
2. **Integration**: Generate JSON suitable for downstream Stage 4C systems
3. **Transparency**: Detailed logging and validation reports
4. **Documentation**: Comprehensive README and inline documentation

## Input Formats

### ENWL Network Asset Viewer

**Format Identifier**: CSV with columns `ENID`, `Support No`

**Expected Columns**:
- ENID: Unique pole identifier (required)
- Support No: Support/asset number (required)
- Easting, Northing: OSGB36 coordinates (required)
- Latitude, Longitude: WGS84 coordinates (optional)
- Feature: Feature classification code
- Voltage: Voltage level (LV/HV/EHV)
- Structure Type: Pole type (POLE/TOWER/COLUMN)
- Status: Service status (ACTIVE/RETIRED/etc)

**Example**:
```
ENID,Support No,Easting,Northing,Latitude,Longitude,Feature,Voltage,Structure Type,Status
16938106,903203,354123.45,456789.12,54.123456,-2.987654,POLE,LV,POLE,ACTIVE
```

### Trimble Survey Export

**Format Identifier**: CSV with columns `Feature Code`, `Point ID`

**Expected Columns**:
- Point ID: Survey point identifier (required)
- Point Name: Field-captured support number (optional)
- Easting, Northing: OSGB36 coordinates (required)
- Feature Code: Feature classification
- Elevation: Height above datum (optional)

**Example**:
```
Feature Code,Point ID,Point Name,Easting,Northing,Elevation
POLE,T001,SP903203,354123.45,456789.12,125.5
```

### Generic/Unknown Format

For unrecognized formats, the parser attempts best-effort mapping:
1. Finds columns containing "east" or "north" for coordinates
2. Looks for "support" or "name" columns for support number
3. Uses first column as pole_id if not found

## Output Format

### JSON Structure

```json
{
  "metadata": {
    "source_file": "baseline.csv",
    "format_detected": "ENWL",
    "ingestion_date": "2026-05-13T14:35:00",
    "total_poles": 150,
    "valid_poles": 148,
    "validation_errors": 2,
    "validation_warnings": 5,
    "has_coordinates": true,
    "has_wgs84": true,
    "has_routes": true,
    "has_sequences": true
  },
  "poles": [
    {
      "pole_id": "16938106",
      "support_no": "903203",
      "easting": 354123.45,
      "northing": 456789.12,
      "latitude": 54.123456,
      "longitude": -2.987654,
      "route_id": "ROUTE_001",
      "pole_sequence": 1,
      "voltage_level": "LV",
      "asset_type": "POLE",
      "feature_code": "ABC123",
      "status": "IN_SERVICE",
      "metadata": {}
    }
  ],
  "validation_report": {
    "total_poles": 150,
    "valid_poles": 148,
    "valid_with_warnings": 2,
    "issues": [...],
    "warnings": [...],
    "errors": [...]
  }
}
```

## Validation Rules

### Required Fields

- `pole_id`: Must be non-empty string (ERROR if missing)
- `easting`: Must be numeric 0-700,000 (ERROR if missing/invalid)
- `northing`: Must be numeric 0-1,300,000 (ERROR if missing/invalid)

### Recommended Fields

- `support_no`: Should be present (WARNING if missing)
- `route_id`: Should be assigned (WARNING if missing)

### Validation Checks

1. **Coordinate Bounds**:
   - OSGB36: Easting 0-700,000 m, Northing 0-1,300,000 m
   - WGS84: Latitude 50-60°, Longitude -8 to 2°

2. **Duplicates**:
   - pole_id: ERROR if duplicate
   - support_no: WARNING if duplicate

3. **Data Types**:
   - Numeric fields must be float/int
   - String fields must be text
   - Enums must be valid value

4. **Support Numbers**:
   - Must follow known format or be marked UNKNOWN
   - Non-numeric variants detected and reported

## Coordinate Transformation

### OSGB36 to WGS84

**Method**: pyproj OSGB36 (EPSG:27700) → WGS84 (EPSG:4326)

**Accuracy**: ±0.01° (~1 km)

**Validation**:
- Input (easting, northing) must be within UK bounds
- Output (latitude, longitude) must be within UK bounds
- Invalid coordinates are flagged and excluded

### Reverse Transformation

WGS84 → OSGB36 supported for validation/testing.

## Support Number Normalization

### Normalization Rules

| Input | Output | Variant |
|-------|--------|---------|
| `903203` | `903203` | None (pure numeric) |
| `SP903203` | `903203` | SP_PREFIX |
| `903201A` | `903201` | SUFFIX_A |
| `90-3203` | `903203` | WITH_SEPARATOR |
| `UNKNOWN` | None | (marked as unknown) |

### Unknown Patterns

Recognized as "no support number":
- UNKNOWN, null, none, N/A, TBD, ? (case-insensitive)
- Empty string

## Route Reconstruction

### Algorithm

When route_id is missing, poles are assigned to synthetic routes using spatial clustering:

1. **Grouping**:
   - Poles with explicit route_id kept together
   - Remaining poles grouped by proximity (max 500m between consecutive poles)

2. **Ordering**:
   - Within each route, poles ordered by nearest-neighbor distance
   - Starting from southernmost pole (smallest northing)

3. **Sequencing**:
   - Assigned sequence numbers 1, 2, 3, ... within route

### Distance Metric

Uses Euclidean distance on OSGB36 grid (sufficient for local UK distances):

```
distance = sqrt((E2-E1)² + (N2-N1)²)
```

### Continuity Validation

Gaps >500m between consecutive poles are flagged:

```python
gaps = reconstructor.validate_route_continuity(poles)
# → [{"from": "POLE_001", "to": "POLE_003", "distance": 1250}]
```

## Error Handling Strategy

### Severity Levels

| Severity | Action | Example |
|----------|--------|---------|
| ERROR | Pole marked invalid, may block processing if --strict | Missing coordinates |
| WARNING | Pole processed, issue recorded | Missing support_no |
| INFO | Logged for debugging | Format detection |

### Graceful Degradation

1. **Malformed rows**: Skipped with warning (processing continues)
2. **Invalid coordinates**: Flagged as ERROR (pole may still be usable)
3. **Missing optional fields**: WARNING only
4. **Encoding issues**: Tried multiple encodings (UTF-8, Latin-1, CP1252)
5. **Unrecognized format**: Falls back to generic parser

### Strict Mode

With `--strict` flag, any ERROR severity validation issue causes exit code 1.

## Performance Requirements

### Targets

| Dataset Size | Time | Target |
|--------------|------|--------|
| 100 poles | <0.5s | CSV parsing |
| 1,000 poles | <5s | Full pipeline |
| 10,000 poles | <60s | Full pipeline |

### Optimization

- Pandas for fast CSV reading (vs manual parsing)
- Vectorized coordinate transformation (batch processing)
- Spatial index for route reconstruction (optional future)

## Testing Strategy

### Coverage Target

≥80% of modules and critical paths

### Test Categories

1. **Parser Tests**: Format detection, field extraction, encoding handling
2. **Validator Tests**: Required fields, coordinates, duplicates
3. **Transformer Tests**: OSGB36↔WGS84 conversion, bounds checking
4. **Normalizer Tests**: Support number variants, unknown patterns
5. **Reconstructor Tests**: Route detection, pole ordering, continuity
6. **Integration Tests**: Full pipeline, CLI validation

### Test Data

- Fixtures: ENWL sample (10 poles), Trimble sample (10 poles)
- Edge cases: Empty CSV, missing headers, malformed rows, invalid coordinates, duplicates

## Dependencies

### Core

- `pandas>=2.0.0`: CSV parsing, data manipulation
- `pydantic>=2.0.0`: Schema validation, type safety
- `pyproj>=3.5.0`: Coordinate transformation
- `python-dateutil>=2.8.0`: Date/time utilities

### Development

- `pytest>=7.0.0`: Testing framework
- `pytest-cov>=4.0.0`: Code coverage
- `black>=23.0.0`: Code formatting
- `mypy>=1.0.0`: Type checking

## Future Enhancements

### Phase 2

1. **Streaming Parser**: Handle datasets >100K poles without loading all into memory
2. **Additional DNO Formats**: NGED, SPEN, SSEN, UKPN, NPG formats
3. **Spatial Index**: k-d tree for faster route reconstruction
4. **Incremental Processing**: Merge new baseline data with existing records
5. **Asset Lifecycle**: Track pole age, replacement plans, decommissioning

### Phase 3

1. **Field Matching**: Integrate with Stage 4C.2 field-capture system
2. **Design Integration**: Export to CAD-ready format
3. **Visualization**: Web-based baseline viewer
4. **Performance Profiling**: Optimize for very large datasets

## Acceptance Criteria

The baseline ingestion engine is considered complete when:

✅ Can parse ENWL, Trimble, and generic CSV formats
✅ Detects format automatically with >95% accuracy
✅ Validates data quality with comprehensive checks
✅ Transforms OSGB36↔WGS84 coordinates
✅ Normalizes support numbers consistently
✅ Reconstructs routes from spatial proximity
✅ Handles 10,000+ pole datasets in <60 seconds
✅ ≥80% pytest coverage
✅ CLI interface works end-to-end
✅ Generates structured JSON output
✅ Produces detailed validation reports
✅ Comprehensive documentation complete

## References

- **pyproj Documentation**: https://pyproj4.github.io/pyproj/stable/
- **OSGB36 Specification**: https://www.ordnancesurvey.co.uk/
- **WGS84 Specification**: https://earth-info.nga.mil/GandG/wgs84/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Pandas Documentation**: https://pandas.pydata.org/

---

**Document Status**: Complete
**Last Updated**: 2026-05-13
**Next Review**: Post-implementation validation
