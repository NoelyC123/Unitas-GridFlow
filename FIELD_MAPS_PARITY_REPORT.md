# Field Maps Display Parity Report

**Date:** 2026-05-01
**Reference:** NIE MV_Poles Field Maps-style 19-field display model

## Parity Status

GridFlow now has display slots for **19/19 Field Maps-style pole fields**. Current survey exports may still leave some fields as `not captured`; that is expected until Stage 4 structured field capture populates them.

## Covered Fields

- OBJECTID / point reference -> `point_id`, `pole_id`, `id`
- Pole number -> `pole_id`
- Status (existing/proposed/recovered/retained) -> `asset_intent`, `lifecycle_state`
- Material -> `material`
- Pole type -> `structure_type`
- Condition -> `condition`
- Grade/class -> `pole_class`
- Height -> `height`
- Year installed -> `year_installed`
- Comments/remarks -> `name`, `remarks`
- Coordinates -> `easting`, `northing`, `lat`, `lon`, `elevation`
- Survey date -> `survey_date`
- Surveyor -> `surveyor`
- Voltage -> `voltage`
- Circuit ID -> `circuit_id`
- Equipment -> `equipment`, `equipment_rating`
- Photos -> `photo_links`, `has_full_pole_photo`, `has_pole_top_photo`, `has_defect_photo`
- Related records -> lifecycle links, replacement links, stay links
- GNSS accuracy -> `gnss_accuracy`

## Current Data Reality

Most current Trimble/controller exports do not contain all Field Maps-style fields. GridFlow therefore displays professional placeholders such as `not captured` while preserving the field structure needed for future tablet/photo workflows.

## Conclusion

GridFlow now reaches Field Maps display parity for available and future-populated survey fields, while adding design-readiness interpretation, QA status, lifecycle links, replacement proximity, stay evidence, and evidence-quality context.
