"""Tests for support number normalizer."""

import pytest

from gridflow.baseline import SupportNumberNormalizer


@pytest.fixture
def normalizer():
    """Return normalizer instance."""
    return SupportNumberNormalizer()


class TestNormalization:
    """Test support number normalization."""

    def test_normalize_pure_numeric(self, normalizer):
        """Test normalization of pure numeric support number."""
        result = normalizer.normalize("903203")
        assert result == "903203"

    def test_normalize_with_prefix(self, normalizer):
        """Test normalization of support number with prefix."""
        result = normalizer.normalize("SP903203")
        assert result == "903203"

    def test_normalize_with_suffix(self, normalizer):
        """Test normalization of support number with suffix."""
        result = normalizer.normalize("903201A")
        assert result == "903201"

    def test_normalize_with_separator(self, normalizer):
        """Test normalization of support number with separator."""
        result = normalizer.normalize("90-3203")
        assert result == "903203"

    def test_normalize_whitespace_and_case(self, normalizer):
        """Test normalization of whitespace and case."""
        result = normalizer.normalize("  SP903203  ")
        assert result == "903203"

    def test_normalize_unknown_patterns(self, normalizer):
        """Test that unknown patterns return None."""
        assert normalizer.normalize("UNKNOWN") is None
        assert normalizer.normalize("null") is None
        assert normalizer.normalize("") is None
        assert normalizer.normalize(None) is None


class TestExtraction:
    """Test numeric extraction."""

    def test_extract_numeric_pure(self, normalizer):
        """Test extraction from pure numeric."""
        result = normalizer.extract_numeric("903203")
        assert result == "903203"

    def test_extract_numeric_mixed(self, normalizer):
        """Test extraction from mixed alphanumeric."""
        result = normalizer.extract_numeric("SP903201A")
        assert result == "903201"

    def test_extract_numeric_no_digits(self, normalizer):
        """Test extraction when no digits present."""
        result = normalizer.extract_numeric("NODIGITS")
        assert result is None


class TestVariantDetection:
    """Test variant format detection."""

    def test_detect_sp_prefix(self, normalizer):
        """Test detection of SP prefix."""
        variant = normalizer.detect_variant("SP903203")
        assert variant == "SP_PREFIX"

    def test_detect_suffix(self, normalizer):
        """Test detection of suffix."""
        variant = normalizer.detect_variant("903201A")
        assert "SUFFIX" in variant

    def test_detect_pure_numeric(self, normalizer):
        """Test that pure numeric has no variant."""
        variant = normalizer.detect_variant("903203")
        assert variant is None


class TestValidation:
    """Test format validation."""

    def test_valid_pure_numeric(self, normalizer):
        """Test validation of pure numeric."""
        assert normalizer.is_valid_format("903203")

    def test_valid_with_prefix(self, normalizer):
        """Test validation with prefix."""
        assert normalizer.is_valid_format("SP903203")

    def test_valid_with_suffix(self, normalizer):
        """Test validation with suffix."""
        assert normalizer.is_valid_format("903201A")

    def test_invalid_no_digits(self, normalizer):
        """Test invalid format with no digits."""
        assert not normalizer.is_valid_format("NODIGITS")

    def test_invalid_unknown_pattern(self, normalizer):
        """Test invalid unknown pattern."""
        assert not normalizer.is_valid_format("@#$%")
