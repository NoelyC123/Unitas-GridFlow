"""
End-to-end tests for the GridFlow unified pipeline (scripts/run_pipeline.py).
"""

import json

# Import main() directly rather than calling subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.run_pipeline import main

BASELINE_FIXTURE = Path(__file__).parent / "baseline" / "fixtures" / "enwl_sample.csv"
# Use the real field dataset if available, otherwise fallback to test fixtures
FIELD_DATASET = Path("real_pilot_data/P_LOCAL_001/enwl_enrichment_clean")
if not FIELD_DATASET.exists():
    FIELD_DATASET = Path(__file__).parent / "field" / "fixtures" / "valid_dataset"


@pytest.fixture
def output_dir(tmp_path):
    """Return a fresh temporary output directory."""
    return tmp_path / "gridflow_output"


def _run_pipeline(args_list: list[str]):
    """Run the pipeline main() with the given argument list."""
    with patch("sys.argv", ["run_pipeline.py"] + args_list):
        return main()


class TestPipelineE2E:
    """End-to-end pipeline tests."""

    def test_pipeline_runs_end_to_end(self, output_dir):
        """Full pipeline produces all expected output files."""
        rc = _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                str(FIELD_DATASET),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        assert rc == 0

        # Find the run directory
        run_dirs = list(output_dir.glob("pipeline_run_*"))
        assert len(run_dirs) == 1
        run_dir = run_dirs[0]

        # Verify all expected files exist
        expected_files = [
            "01_baseline_dataset.json",
            "02_field_dataset.json",
            "03_match_register.json",
            "03_match_register.csv",
            "04_merged_dataset.json",
            "04_merged_dataset.csv",
            "05_qa_report.md",
            "pipeline_summary.json",
        ]
        for fname in expected_files:
            assert (run_dir / fname).exists(), f"Missing output file: {fname}"

    def test_pipeline_summary_json_structure(self, output_dir):
        """pipeline_summary.json has all required fields."""
        _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                str(FIELD_DATASET),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        run_dir = sorted(output_dir.glob("pipeline_run_*"))[0]
        summary_path = run_dir / "pipeline_summary.json"

        with open(summary_path) as f:
            summary = json.load(f)

        required_keys = [
            "run_id",
            "run_date",
            "baseline_source",
            "field_source",
            "baseline_format_detected",
            "duration_seconds",
            "stages",
            "overall_status",
            "match_rate",
            "design_ready_count",
            "design_blocked_count",
            "output_directory",
        ]
        for key in required_keys:
            assert key in summary, f"Missing key in summary: {key}"

        assert summary["overall_status"] == "PASS"

    def test_pipeline_output_directory_created(self, output_dir):
        """A timestamped run directory is created under output/."""
        assert not output_dir.exists()  # Starts non-existent
        _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                str(FIELD_DATASET),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        assert output_dir.exists()
        run_dirs = list(output_dir.glob("pipeline_run_*"))
        assert len(run_dirs) == 1

    def test_pipeline_stage_timing(self, output_dir):
        """pipeline_summary.json records duration_seconds for all stages."""
        _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                str(FIELD_DATASET),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        run_dir = sorted(output_dir.glob("pipeline_run_*"))[0]
        with open(run_dir / "pipeline_summary.json") as f:
            summary = json.load(f)

        stages = summary["stages"]
        for stage_key in ("baseline_ingest", "field_import", "matching", "merge"):
            assert stage_key in stages
            assert "duration_seconds" in stages[stage_key]
            assert stages[stage_key]["duration_seconds"] >= 0

    def test_pipeline_format_detection(self, output_dir):
        """ENWL format is auto-detected from the fixture CSV."""
        _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                str(FIELD_DATASET),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        run_dir = sorted(output_dir.glob("pipeline_run_*"))[0]
        with open(run_dir / "pipeline_summary.json") as f:
            summary = json.load(f)
        assert summary["baseline_format_detected"] == "ENWL"


class TestPipelineErrorHandling:
    """Tests for pipeline error handling and clean failure."""

    def test_pipeline_handles_missing_baseline(self, output_dir):
        """Pipeline exits cleanly when baseline CSV not found."""
        rc = _run_pipeline(
            [
                "--baseline",
                "/nonexistent/baseline.csv",
                "--field",
                str(FIELD_DATASET),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        assert rc == 1

    def test_pipeline_handles_missing_field(self, output_dir):
        """Pipeline exits cleanly when field folder not found."""
        rc = _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                "/nonexistent/field/",
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        assert rc == 1

    def test_pipeline_handles_empty_field(self, tmp_path, output_dir):
        """Pipeline handles empty field folder gracefully."""
        empty_field = tmp_path / "empty_field"
        empty_field.mkdir()
        rc = _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                str(empty_field),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        # Should complete (0 poles matched) without crashing
        assert rc == 0
        run_dir = sorted(output_dir.glob("pipeline_run_*"))[0]
        assert (run_dir / "pipeline_summary.json").exists()

    def test_pipeline_partial_output_on_stage2_fail(self, tmp_path, output_dir):
        """Stage 1 output is preserved even when Stage 2 fails."""
        fake_field = tmp_path / "not_a_real_folder_xyz"
        rc = _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                str(fake_field),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        assert rc == 1
        run_dirs = list(output_dir.glob("pipeline_run_*"))
        if run_dirs:
            run_dir = run_dirs[0]
            # Stage 1 should have saved its output before stage 2 failed
            assert (run_dir / "01_baseline_dataset.json").exists()


class TestPipelineOutputContent:
    """Tests for the content of pipeline outputs."""

    def test_baseline_dataset_json_has_poles(self, output_dir):
        """01_baseline_dataset.json contains expected pole count."""
        _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                str(FIELD_DATASET),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        run_dir = sorted(output_dir.glob("pipeline_run_*"))[0]
        with open(run_dir / "01_baseline_dataset.json") as f:
            data = json.load(f)
        assert "poles" in data
        assert len(data["poles"]) == 10

    def test_qa_report_is_markdown(self, output_dir):
        """05_qa_report.md is valid markdown with expected sections."""
        _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                str(FIELD_DATASET),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        run_dir = sorted(output_dir.glob("pipeline_run_*"))[0]
        report_text = (run_dir / "05_qa_report.md").read_text()

        assert "GridFlow QA Report" in report_text
        assert "Design Blockers" in report_text
        assert "Recommended Next Steps" in report_text
        assert "Unmatched Poles" in report_text

    def test_stage5a_reports_are_generated(self, output_dir):
        """Stage 5A emits pilot output pack reports 06, 07, and 08."""
        _run_pipeline(
            [
                "--baseline",
                str(BASELINE_FIXTURE),
                "--field",
                str(FIELD_DATASET),
                "--output",
                str(output_dir),
                "--log-level",
                "WARNING",
            ]
        )
        run_dir = sorted(output_dir.glob("pipeline_run_*"))[0]
        expected = [
            "06_dno_data_request.md",
            "07_design_readiness_summary.md",
            "08_match_confidence_analysis.md",
        ]
        for filename in expected:
            path = run_dir / filename
            assert path.exists()
            assert len(path.read_text(encoding="utf-8")) > 500
