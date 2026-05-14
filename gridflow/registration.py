"""Pipeline output registration for GridFlow web review routes.

Copies a completed pipeline run into ``uploads/jobs/<job_id>/`` so the
workspace and map routes can read the output immediately.
"""

from __future__ import annotations

import json
import logging
import shutil
import string
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

_SAFE_JOB_CHARS = set(string.ascii_letters + string.digits + "-_")


def generate_job_id() -> str:
    """Generate a timestamp-based job ID."""
    return f"gridflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _sanitise_job_id(job_id: str) -> str:
    """Return a filesystem-safe job ID using only alphanumerics, hyphens, underscores."""
    return "".join(c if c in _SAFE_JOB_CHARS else "_" for c in job_id)


def register_pipeline_output(
    pipeline_run_dir: Path,
    job_id: str,
    jobs_root: Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Copy pipeline output into ``uploads/jobs/<job_id>/`` for web access.

    Args:
        pipeline_run_dir: Completed ``pipeline_run_*`` directory to register.
        job_id: Job ID to register under.
        jobs_root: Root jobs directory. Defaults to ``uploads/jobs``.
        overwrite: Replace an existing registered job when true.

    Returns:
        Registered job directory.

    Raises:
        FileNotFoundError: If ``pipeline_run_dir`` does not exist.
        FileExistsError: If the job directory already exists and ``overwrite`` is false.
        ValueError: If ``job_id`` is empty.
    """
    pipeline_run_dir = Path(pipeline_run_dir)
    if not pipeline_run_dir.exists():
        raise FileNotFoundError(f"Pipeline run directory not found: {pipeline_run_dir}")

    if not job_id or not job_id.strip():
        raise ValueError("job_id must be a non-empty string")

    safe_job_id = _sanitise_job_id(job_id.strip())
    if safe_job_id != job_id:
        logger.warning("job_id sanitised: %r -> %r", job_id, safe_job_id)
        job_id = safe_job_id

    if jobs_root is None:
        jobs_root = Path("uploads/jobs")
    jobs_root = Path(jobs_root)
    job_dir = jobs_root / job_id

    if job_dir.exists():
        if not overwrite:
            raise FileExistsError(
                f"Job '{job_id}' already exists at {job_dir}. "
                "Use --overwrite-registration to replace it."
            )
        logger.warning("Job directory already exists, overwriting: %s", job_dir)
        shutil.rmtree(job_dir)

    logger.info("Registering pipeline output as job: %s", job_id)
    shutil.copytree(pipeline_run_dir, job_dir)
    logger.info("Copied %s -> %s", pipeline_run_dir, job_dir)

    meta = {
        "job_id": job_id,
        "registered_at": datetime.now().isoformat(),
        "pipeline_run_dir": str(pipeline_run_dir),
        "source": "pipeline_registration",
    }
    meta_path = job_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logger.info("Written meta.json: %s", meta_path)

    return job_dir


def print_registration_summary(job_id: str, job_dir: Path) -> None:
    """Print web routes for a registered job."""
    base = "http://127.0.0.1:5000"
    print("\n" + "=" * 60)
    print(f"Registered as job: {job_id}")
    print(f"   Location: {job_dir}")
    print()
    print("   Web interface (start Flask first):")
    print(f"   Workspace:  {base}/workspace/view/{job_id}")
    print(f"   Overlay:    {base}/map/overlay/{job_id}")
    print(f"   QA Map:     {base}/map/view/{job_id}")
    print("=" * 60 + "\n")
