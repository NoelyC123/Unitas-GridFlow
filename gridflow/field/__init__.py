"""
GridFlow Field Evidence Importer (Stage 4C.2)

Scans, parses, and validates field evidence from pole survey folders.
"""

from gridflow.field.dataset_validator import FieldDatasetValidator
from gridflow.field.evidence_quality_scorer import EvidenceQualityScorer
from gridflow.field.folder_scanner import FolderScanner
from gridflow.field.models import FieldDataset, FieldPole
from gridflow.field.notes_parser import NotesParser

__version__ = "0.1.0"
__all__ = [
    "FieldPole",
    "FieldDataset",
    "FolderScanner",
    "NotesParser",
    "EvidenceQualityScorer",
    "FieldDatasetValidator",
]
