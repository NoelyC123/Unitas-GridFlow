"""
GridFlow Matching Engine (Stage 4C.3)

Correlates baseline poles to field evidence using support number matching
and confidence scoring.
"""

from gridflow.matching.confidence_scorer import ConfidenceScorer
from gridflow.matching.models import MatchRegister, MatchRegisterEntry, MatchResult
from gridflow.matching.register_builder import RegisterBuilder
from gridflow.matching.support_number_matcher import SupportNumberMatcher

__version__ = "0.1.0"
__all__ = [
    "MatchResult",
    "MatchRegister",
    "MatchRegisterEntry",
    "SupportNumberMatcher",
    "ConfidenceScorer",
    "RegisterBuilder",
]
