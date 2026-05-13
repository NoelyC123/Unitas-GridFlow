"""
GridFlow Baseline Ingestion Engine (Stage 4C.1)

A production-grade system for parsing, validating, and normalizing DNO/Trimble
baseline CSV exports for overhead line infrastructure.

Public API exports all major classes and functions for easy access.
"""

from gridflow.baseline.coordinate_transformer import CoordinateTransformer
from gridflow.baseline.csv_parser import CSVParser
from gridflow.baseline.models import (
    AssetStatus,
    AssetType,
    BaselineDataset,
    BaselinePole,
    ValidationIssue,
    ValidationReport,
    VoltageLevel,
)
from gridflow.baseline.route_reconstructor import RouteReconstructor
from gridflow.baseline.schema_validator import SchemaValidator
from gridflow.baseline.support_number_normalizer import SupportNumberNormalizer

__version__ = "0.1.0"
__all__ = [
    "BaselinePole",
    "BaselineDataset",
    "ValidationIssue",
    "ValidationReport",
    "VoltageLevel",
    "AssetType",
    "AssetStatus",
    "CSVParser",
    "SchemaValidator",
    "CoordinateTransformer",
    "SupportNumberNormalizer",
    "RouteReconstructor",
]
