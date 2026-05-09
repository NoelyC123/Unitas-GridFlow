/**
 * Frontend field display helpers for C2E2 popup expansion.
 * Mirrors app/field_validators.py for JavaScript use.
 *
 * Based on field_reference.py definitions and field_validators.py logic.
 * Codex can import these or implement directly in map-viewer.js.
 */

// Field groups from field_reference.py POPUP_FIELD_GROUPS
const FIELD_GROUPS = {
  identity: ['pole_id', 'structure_type', 'asset_intent', 'record_role'],
  geometry: ['easting', 'northing', 'height'],
  quality: ['qa_status', 'issue_count', 'warn_count'],
  survey_context: ['name', 'material', 'land_use'],
  relationship: ['relationship', 'being_replaced_by', 'replacing'],
};

// Ordered group display sequence
const FIELD_GROUP_ORDER = [
  'identity',
  'geometry',
  'quality',
  'survey_context',
  'relationship',
];

// Display labels from field_reference.py FIELD_DEFINITIONS
const FIELD_LABELS = {
  pole_id: 'Point ID',
  structure_type: 'Feature Code',
  asset_intent: 'Asset Intent',
  record_role: 'Record Role',
  easting: 'Easting',
  northing: 'Northing',
  height: 'Measured Height',
  qa_status: 'QA Status',
  issue_count: 'Issues',
  warn_count: 'Warnings',
  name: 'Survey Note',
  material: 'Material',
  land_use: 'Land Use',
  relationship: 'Relationship',
  being_replaced_by: 'Being Replaced By',
  replacing: 'Replacing',
};

// Units from field_reference.py
const FIELD_UNITS = {
  height: 'm',
  easting: 'm',
  northing: 'm',
};

// Aliases from field_reference.py
const FIELD_ALIASES = {
  height: ['h', 'ht', 'elev', 'elevation', 'pole_height', 'heights'],
  easting: ['e', 'east', 'osgb_e', 'osgb_east', 'grid_east', 'x'],
  northing: ['n', 'north', 'osgb_n', 'osgb_north', 'grid_north', 'y'],
  name: ['location', 'remark', 'remarks', 'note', 'notes', 'description', 'comment', 'desc'],
};

// Missing-value wording from field_reference.py conditional_missing
const MISSING_WORDING = {
  height: {
    Pol: 'Not measured (intermediate pole)',
    EXpole: 'Not measured — check survey notes',
    Angle: 'Not measured — check survey notes',
    EXangle: 'Not measured — check survey notes',
    PRpole: 'Not measured',
    PRangle: 'Not measured',
    _default: 'Not measured',
  },
  material: {
    _default: 'Not recorded in survey',
  },
  name: {
    _default: '—',
  },
  relationship: {
    _default: '—',
  },
  being_replaced_by: {
    _default: '—',
  },
  replacing: {
    _default: '—',
  },
  land_use: {
    _default: 'Not recorded',
  },
};

/**
 * Check if a value is measured (non-null, non-empty, non-NaN).
 * Mirrors field_validators.is_measured()
 */
function isMeasured(value) {
  if (value === null || value === undefined) return false;
  if (value === '' || value === 'nan') return false;
  if (typeof value === 'number' && isNaN(value)) return false;
  if (typeof value === 'string' && value.trim() === '') return false;
  return true;
}

/**
 * Get missing-value wording for a field based on structure type.
 * Mirrors field_reference.get_missing_wording()
 */
function getMissingWording(fieldName, structureType = null) {
  const wordingMap = MISSING_WORDING[fieldName];
  if (!wordingMap) return '—';

  if (structureType && wordingMap[structureType]) {
    return wordingMap[structureType];
  }

  return wordingMap._default || '—';
}

/**
 * Format a field value for display (with unit, missing wording).
 * Mirrors field_validators.format_field_display()
 */
function formatFieldDisplay(value, fieldName, structureType = null) {
  if (!isMeasured(value)) {
    return getMissingWording(fieldName, structureType);
  }

  const unit = FIELD_UNITS[fieldName];
  const numValue = parseFloat(value);

  if (unit && !isNaN(numValue)) {
    // Remove trailing zeros: 9.0 → "9", 9.2 → "9.2"
    const formatted = numValue % 1 === 0 ? numValue.toFixed(0) : String(numValue);
    return `${formatted}${unit}`;
  }

  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }

  return String(value).trim() || getMissingWording(fieldName, structureType);
}

/**
 * Get display label for a field.
 * Mirrors field_reference.get_display_label()
 */
function getFieldLabel(fieldName) {
  return (
    FIELD_LABELS[fieldName] ||
    fieldName.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
  );
}

/**
 * Get all fields for a popup group.
 * Mirrors field_reference.get_fields_for_group()
 */
function getFieldsForGroup(groupName) {
  return FIELD_GROUPS[groupName] || [];
}

/**
 * Resolve alias to canonical field name.
 * Mirrors field_reference.resolve_alias()
 */
function resolveAlias(columnName) {
  const lower = columnName.toLowerCase().trim();

  for (const fieldName of Object.keys(FIELD_LABELS)) {
    if (lower === fieldName.toLowerCase()) {
      return fieldName;
    }
  }

  for (const [fieldName, aliases] of Object.entries(FIELD_ALIASES)) {
    if (aliases.some((a) => a.toLowerCase() === lower)) {
      return fieldName;
    }
  }

  return null;
}

/**
 * Get popup display value from feature properties with alias resolution.
 * Mirrors field_validators.get_popup_display_value()
 */
function getPopupDisplayValue(fieldName, properties, structureType = null) {
  let value = properties[fieldName];

  if (!isMeasured(value)) {
    const aliases = FIELD_ALIASES[fieldName] || [];
    for (const alias of aliases) {
      const candidate = properties[alias];
      if (isMeasured(candidate)) {
        value = candidate;
        break;
      }
    }
  }

  if (!structureType) {
    structureType = properties.structure_type || null;
  }

  return formatFieldDisplay(value, fieldName, structureType);
}

// Export for Node.js / test environment
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    FIELD_GROUPS,
    FIELD_GROUP_ORDER,
    FIELD_LABELS,
    FIELD_UNITS,
    FIELD_ALIASES,
    MISSING_WORDING,
    isMeasured,
    getMissingWording,
    formatFieldDisplay,
    getFieldLabel,
    getFieldsForGroup,
    resolveAlias,
    getPopupDisplayValue,
  };
}
