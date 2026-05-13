"""
GridFlow Merge Engine (Stage 4C.4)

Combines baseline, field, and matching evidence into a designer-ready
MergedDataset with verification flags and QA report.
"""

from gridflow.merge.models import MergedPole, MergedDataset
from gridflow.merge.data_merger import DataMerger
from gridflow.merge.verification_flag_generator import VerificationFlagGenerator
from gridflow.merge.conflict_detector import ConflictDetector
from gridflow.merge.qa_report_generator import QAReportGenerator

__version__ = "0.1.0"
__all__ = [
    "MergedPole",
    "MergedDataset",
    "DataMerger",
    "VerificationFlagGenerator",
    "ConflictDetector",
    "QAReportGenerator",
]
