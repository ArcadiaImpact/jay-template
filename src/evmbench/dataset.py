"""Dataset loading for EVMbench evaluation.

Downloads and caches audit data from the OpenAI frontier-evals repository,
parses vulnerability metadata, and constructs Inspect Samples with per-sample
Docker sandbox specifications.
"""

import csv
import io
import json
import logging
import zipfile
from pathlib import Path
from typing import Any

import requests
import yaml
from inspect_ai.dataset import MemoryDataset, Sample

from evmbench.constants import (
    AUDIT_DIR,
    CACHE_DIR,
    EVMBENCH_COMMIT_SHA,
    EVMBENCH_REPO,
    EVMBENCH_SUBDIR,
    EXPLOIT_CHAIN_ID,
    EXPLOIT_RPC_PORT,
    EXPLOIT_WALLET_ADDRESS,
    EXPLOIT_WALLET_PRIVATE_KEY,
    SUBMISSION_DIR,
    TaskType,
)
from evmbench.docker import ensure_base_images, get_sandbox_spec
from evmbench.prompts import PromptMode, get_prompt

logger = logging.getLogger(__name__)


def load_evmbench_dataset(
    task_type: TaskType,
    prompt_mode: PromptMode = "improved",
    split: str | None = None,
    audit_ids: list[str] | None = None,
) -> MemoryDataset:
    """Load the EVMbench dataset for a given task type.

    Args:
        task_type: One of "detect", "patch", "exploit".
        prompt_mode: "original" or "improved" prompt templates.
        split: Optional split file name (e.g., "detect-tasks", "patch-tasks").
        audit_ids: Optional list of specific audit IDs to include.

    Returns:
        A MemoryDataset of Sample objects with per-sample sandbox specs.
    """
    data_dir = _ensure_data()
    ensure_base_images(data_dir)
    records = _parse_task_info(data_dir)

    # Filter by split file
    if split is not None:
        split_ids = _load_split(split, data_dir)
        records = [r for r in records if r["audit_id"] in split_ids]

    # Filter by audit IDs
    if audit_ids is not None:
        audit_set = set(audit_ids)
        records = [r for r in records if r["audit_id"] in audit_set]

    # Filter by task type availability using per-audit config
    if task_type == "exploit":
        filtered = []
        for record in records:
            audit_id = record.get("audit_id", "")
            vuln_id = record.get("vulnerability_id", "")
            audit_dir = data_dir / "audits" / audit_id
            if audit_dir.exists():
                config = _load_audit_config(audit_dir)
                vuln_info = _find_vulnerability(config, vuln_id)
                if vuln_info.get("exploit_task", False):
                    filtered.append(record)
        records = filtered

    samples = []
    for record in records:
        sample = _record_to_sample(record, task_type, prompt_mode, data_dir)
        if sample is not None:
            samples.append(sample)

    logger.info(
        "Loaded %d samples for task_type=%s, prompt_mode=%s",
        len(samples),
        task_type,
        prompt_mode,
    )
    return MemoryDataset(samples=samples, name=f"evmbench_{task_type}")


def _ensure_data(force_download: bool = False) -> Path:
    """Download and cache EVMbench audit data from GitHub.

    Args:
        force_download: If True, re-download even if cached.

    Returns:
        Path to the extracted data directory.
    """
    data_dir = CACHE_DIR / "data"
    marker = data_dir / ".download_complete"

    if marker.exists() and not force_download:
        return data_dir

    data_dir.mkdir(parents=True, exist_ok=True)

    url = f"https://github.com/{EVMBENCH_REPO}/archive/{EVMBENCH_COMMIT_SHA}.zip"
    logger.info("Downloading EVMbench data from %s", url)
    response = requests.get(url, timeout=300)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        # The zip contains a top-level dir like "frontier-evals-<sha>/"
        prefix = f"frontier-evals-{EVMBENCH_COMMIT_SHA}/{EVMBENCH_SUBDIR}/"
        for info in zf.infolist():
            if not info.filename.startswith(prefix):
                continue
            # Strip the prefix to get the relative path
            rel_path = info.filename[len(prefix) :]
            if not rel_path:
                continue
            target = data_dir / rel_path
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src, open(target, "wb") as dst:
                    dst.write(src.read())

    _apply_patches(data_dir)
    marker.touch()
    logger.info("EVMbench data extracted to %s", data_dir)
    return data_dir


def _apply_patches(data_dir: Path) -> None:
    """Apply fixes to upstream data that haven't been merged yet."""
    # 2024-03-taiko: COPY doesn't preserve execute bit, so invoke via bash
    # https://github.com/openai/frontier-evals — pending upstream fix
    taiko_dockerfile = data_dir / "audits" / "2024-03-taiko" / "Dockerfile"
    if taiko_dockerfile.exists():
        content = taiko_dockerfile.read_text()
        patched = content.replace(
            "RUN ./replace_symlinks_with_real_files.sh",
            "RUN bash ./replace_symlinks_with_real_files.sh",
        )
        if patched != content:
            taiko_dockerfile.write_text(patched)
            logger.info("Patched 2024-03-taiko Dockerfile (permission fix)")

    # 2024-06-thorchain: hardhat tests fail at build time (exit code 8),
    # blocking image creation. Tests should be run by the agent, not as a
    # build gate.
    thorchain_dockerfile = data_dir / "audits" / "2024-06-thorchain" / "Dockerfile"
    if thorchain_dockerfile.exists():
        content = thorchain_dockerfile.read_text()
        patched = content.replace(
            "RUN npx hardhat test\n",
            "RUN npx hardhat test || true\n",
        )
        if patched != content:
            thorchain_dockerfile.write_text(patched)
            logger.info("Patched 2024-06-thorchain Dockerfile (allow test failures)")


def _parse_task_info(data_dir: Path) -> list[dict[str, Any]]:
    """Parse audits/task_info.csv for vulnerability metadata.

    Args:
        data_dir: Path to the extracted EVMbench data directory.

    Returns:
        List of dicts with vulnerability metadata.
    """
    csv_path = data_dir / "audits" / "task_info.csv"
    if not csv_path.exists():
        logger.warning("task_info.csv not found at %s", csv_path)
        return []

    records: list[dict[str, Any]] = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            record: dict[str, Any] = dict(row)
            # Normalize field names (CSV uses "audit"/"vuln", we use "audit_id"/"vulnerability_id")
            if "audit" in record and "audit_id" not in record:
                record["audit_id"] = record["audit"]
            if "vuln" in record and "vulnerability_id" not in record:
                record["vulnerability_id"] = record["vuln"]
            # Parse numeric fields
            if "award" in record:
                try:
                    record["award"] = float(record["award"])
                except (ValueError, TypeError):
                    record["award"] = 0.0
            # Parse boolean fields
            if "exploit_task" in record:
                record["exploit_task"] = str(record["exploit_task"]).lower() in (
                    "true",
                    "1",
                    "yes",
                )
            records.append(record)

    return records


def _load_audit_config(audit_dir: Path) -> dict[str, Any]:
    """Parse a per-audit config.yaml file.

    Args:
        audit_dir: Path to the specific audit directory.

    Returns:
        Parsed config dict with vulnerability definitions, test commands, etc.
    """
    config_path = audit_dir / "config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def _load_split(split_name: str, data_dir: Path) -> set[str]:
    """Load a split file listing audit IDs.

    Args:
        split_name: Name of the split (e.g., "detect-tasks", "all").
        data_dir: Path to the extracted EVMbench data directory.

    Returns:
        Set of audit IDs in the split.
    """
    # Try with and without .txt extension
    for suffix in [".txt", ""]:
        split_path = data_dir / "splits" / f"{split_name}{suffix}"
        if split_path.exists():
            return {
                line.strip()
                for line in split_path.read_text().splitlines()
                if line.strip()
            }

    logger.warning("Split file '%s' not found in %s/splits/", split_name, data_dir)
    return set()


def _record_to_sample(
    record: dict[str, Any],
    task_type: TaskType,
    prompt_mode: PromptMode,
    data_dir: Path,
) -> Sample | None:
    """Convert a vulnerability record to an Inspect Sample.

    Args:
        record: Vulnerability metadata from task_info.csv.
        task_type: One of "detect", "patch", "exploit".
        prompt_mode: "original" or "improved".
        data_dir: Path to the extracted data directory.

    Returns:
        A Sample with per-sample sandbox spec, or None if the audit
        directory doesn't exist.
    """
    audit_id = record.get("audit_id", "")
    vuln_id = record.get("vulnerability_id", record.get("vuln_id", ""))
    audit_dir_path = data_dir / "audits" / audit_id

    if not audit_dir_path.exists():
        logger.warning("Audit directory not found: %s", audit_dir_path)
        return None

    # Load per-audit config for detailed vulnerability info
    audit_config = _load_audit_config(audit_dir_path)

    # Find vulnerability details in config
    vuln_info = _find_vulnerability(audit_config, vuln_id)
    vuln_description = vuln_info.get(
        "title", record.get("title", f"Vulnerability {vuln_id}")
    )

    # Build the prompt with template variables
    prompt_template = get_prompt(task_type, prompt_mode)
    prompt_vars: dict[str, Any] = {
        "audit_dir": AUDIT_DIR,
        "submission_dir": SUBMISSION_DIR,
        "vulnerability_description": vuln_description,
        "rpc_port": str(EXPLOIT_RPC_PORT),
        "chain_id": str(EXPLOIT_CHAIN_ID),
        "wallet_address": EXPLOIT_WALLET_ADDRESS,
        "wallet_private_key": EXPLOIT_WALLET_PRIVATE_KEY,
    }
    # Only format variables that exist in the template
    prompt = prompt_template
    for key, value in prompt_vars.items():
        placeholder = "{" + key + "}"
        if placeholder in prompt:
            prompt = prompt.replace(placeholder, str(value))

    # Build target (ground truth for scoring)
    target = _build_target(record, task_type, vuln_info, audit_config)

    # Get per-sample sandbox spec
    sandbox = get_sandbox_spec(audit_id, task_type, data_dir)

    return Sample(
        input=prompt,
        target=target,
        id=f"{audit_id}/{vuln_id}",
        metadata={
            "audit_id": audit_id,
            "vulnerability_id": vuln_id,
            "award_usd": record.get("award", 0.0),
            "framework": audit_config.get("framework", "unknown"),
            "task_type": task_type,
        },
        sandbox=sandbox,
    )


def _find_vulnerability(audit_config: dict[str, Any], vuln_id: str) -> dict[str, Any]:
    """Find a specific vulnerability in the audit config.

    Args:
        audit_config: Parsed config.yaml for the audit.
        vuln_id: Vulnerability identifier (e.g., "H-01").

    Returns:
        Vulnerability info dict, or empty dict if not found.
    """
    vulnerabilities = audit_config.get("vulnerabilities", [])
    if isinstance(vulnerabilities, list):
        for vuln in vulnerabilities:
            if isinstance(vuln, dict) and vuln.get("id") == vuln_id:
                return vuln
    elif isinstance(vulnerabilities, dict):
        result = vulnerabilities.get(vuln_id, {})
        return result if isinstance(result, dict) else {}
    return {}


def _build_target(
    record: dict[str, Any],
    task_type: TaskType,
    vuln_info: dict[str, Any],
    audit_config: dict[str, Any],
) -> str:
    """Build the target string for scoring.

    Args:
        record: Vulnerability metadata.
        task_type: One of "detect", "patch", "exploit".
        vuln_info: Detailed vulnerability info from config.yaml.
        audit_config: Full audit config.

    Returns:
        JSON-encoded target string with scoring information.
    """
    audit_id = record.get("audit_id", "")
    vuln_id = record.get("vulnerability_id", record.get("vuln_id", ""))

    base = {
        "audit_id": audit_id,
        "vulnerability_id": vuln_id,
        "title": vuln_info.get("title", record.get("title", "")),
        "award_usd": record.get("award", 0.0),
    }

    if task_type == "detect":
        base["findings"] = vuln_info.get("title", "")
        # Include description from CSV for richer grading context
        base["description"] = record.get("description", vuln_info.get("title", ""))

    elif task_type == "patch":
        # Include test command for the scorer to execute
        framework = audit_config.get("framework", "foundry")
        test_name = vuln_info.get("test", "")
        test_flags = audit_config.get("default_test_flags", "")
        run_cmd_dir = audit_config.get("run_cmd_dir", "")

        if "foundry" in framework:
            test_cmd = f"cd {AUDIT_DIR}/{run_cmd_dir} && forge test --match-test {test_name} {test_flags}"
        else:
            test_cmd = f"cd {AUDIT_DIR}/{run_cmd_dir} && npx hardhat test {test_flags}"

        base["test_command"] = test_cmd
        base["test_name"] = test_name
        base["test_passes_if_vulnerable"] = vuln_info.get(
            "test_passes_if_vulnerable", True
        )

    elif task_type == "exploit":
        base["exploit_task"] = vuln_info.get("exploit_task", True)

    return json.dumps(base)
