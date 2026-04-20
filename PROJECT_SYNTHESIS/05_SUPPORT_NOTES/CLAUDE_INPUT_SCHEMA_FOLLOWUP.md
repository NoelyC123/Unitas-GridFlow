# Claude Input Schema Follow-up

Source: Claude follow-up implementation-spec response

Date: 2026-04-19

---

---

## 1. Canonical sample CSV column list

```
asset_id, structure_type, height_m, material, location_name, easting, northing, latitude, longitude
```

These are the exact column names the new `mock_survey.csv` will use. They reflect the naming conventions common to UK overhead line field survey exports (e.g. from Survitec, or a network operator GIS export). No invented or ambiguous names.

---

## 2. Five sample rows

```csv
asset_id,structure_type,height_m,material,location_name,easting,northing,latitude,longitude
P-1001,Wood Pole,11.0,Wood,Dalton Road Junction,352841,503122,54.5210,-3.0140
P-1002,Wood Pole,7.5,Wood,Back Lane Farm,352910,503088,54.5183,-3.0121
P-1003,Steel Pole,28.0,Steel,Moorside Substation,352975,503200,54.5291,-3.0098
P-1004,Wood Pole,12.5,,Hartley Bridge,353041,503155,54.5246,-3.0075
P-1001,Wood Pole,13.0,Wood,Dalton Road Junction North,353100,503170,54.5261,-3.0052
```

Row-by-row intent:

| Row | Pole | Expected QA result |
|---|---|---|
| 1 | P-1001, height 11.0m, Wood | PASS |
| 2 | P-1002, height 7.5m | FAIL — height below minimum (10m) |
| 3 | P-1003, height 28.0m | FAIL — height above maximum (25m) |
| 4 | P-1004, material blank | FAIL — missing required field |
| 5 | P-1001 again | FAIL — duplicate `asset_id` |

---

## 3. Exact normalization target mapping

| CSV column | Maps to internal field | Notes |
|---|---|---|
| `asset_id` | `pole_id` | Direct rename |
| `height_m` | `height` | Direct rename; coerced to numeric |
| `material` | `material` | Same name, no rename needed |
| `location_name` | `location` | Direct rename |
| `latitude` | `lat` | Direct rename; coerced to numeric |
| `longitude` | `lon` | Direct rename; coerced to numeric |
| `structure_type` | *(unused by QA rules currently)* | Pass through as-is; do not drop |
| `easting` | *(unused by QA rules currently)* | Pass through as-is; do not drop |
| `northing` | *(unused by QA rules currently)* | Pass through as-is; do not drop |

The updated `copy_if_missing` calls for each target field should be:

```python
copy_if_missing("pole_id",  ["asset_id", "pole_id"])
copy_if_missing("height",   ["height_m", "height", "pole_height_m", "pole_height"])
copy_if_missing("material", ["material", "pole_material"])
copy_if_missing("location", ["location_name", "location"])
copy_if_missing("lat",      ["latitude", "lat"])
copy_if_missing("lon",      ["longitude", "lon"])
```

Candidate order is deliberate: the new canonical schema name comes first in each list so it resolves immediately on the new sample CSV, with the old internal name as a secondary fallback only.

---

## 4. What must be removed from `_normalize_dataframe()`

Delete these two candidates from the `height` `copy_if_missing` call:

```python
"clearance_m",    # sample_data fallback for MVP demo   ← DELETE
"pole_spacing_m"  # secondary fallback                  ← DELETE
```

Delete these candidates from the `material` call (they were guessing at non-material columns):

```python
"type"  # too ambiguous — could be structure_type, not material ← DELETE
```

Delete these candidates from the `location` call:

```python
"name",     # too generic ← DELETE
"site",     # not a standard field in this schema ← DELETE
"address",  # not a standard field in this schema ← DELETE
```

Delete these candidates from the `pole_id` call:

```python
"poleid",   # non-standard, no longer needed ← DELETE
"id",       # too generic ← DELETE
"pole",     # too generic ← DELETE
```

After the deletions, the candidate lists are shorter, explicit, and directly grounded in the new canonical schema. Nothing is guessing at surrogate fields.
