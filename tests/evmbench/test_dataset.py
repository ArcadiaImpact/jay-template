"""Tests for EVMbench dataset loading."""

from typing import Any
from unittest.mock import patch

from evmbench.dataset import (
    _build_target,
    _find_vulnerability,
    _record_to_sample,
)


def _make_record(
    audit_id: str = "2023-07-pooltogether",
    vuln_id: str = "H-01",
    title: str = "Deposit Theft via Burn Truncation",
    award: float = 2181.44,
    exploit_task: bool = True,
) -> dict[str, Any]:
    return {
        "audit_id": audit_id,
        "vulnerability_id": vuln_id,
        "title": title,
        "award": award,
        "exploit_task": exploit_task,
    }


def _make_audit_config() -> dict[str, Any]:
    return {
        "id": "2023-07-pooltogether",
        "framework": "foundry-json",
        "run_cmd_dir": "vault",
        "default_test_flags": "--silent",
        "vulnerabilities": [
            {
                "id": "H-01",
                "title": "Deposit Theft via Burn Truncation",
                "test": "ExploitH01.t.sol",
                "test_passes_if_vulnerable": True,
                "award": 2181.44,
                "exploit_task": True,
            },
            {
                "id": "H-02",
                "title": "Vault Share Manipulation",
                "test": "ExploitH02.t.sol",
                "test_passes_if_vulnerable": True,
                "award": 1500.0,
                "exploit_task": False,
            },
        ],
    }


def test_find_vulnerability_found() -> None:
    config = _make_audit_config()
    result = _find_vulnerability(config, "H-01")
    assert result["title"] == "Deposit Theft via Burn Truncation"


def test_find_vulnerability_not_found() -> None:
    config = _make_audit_config()
    result = _find_vulnerability(config, "H-99")
    assert result == {}


def test_find_vulnerability_dict_format() -> None:
    config = {
        "vulnerabilities": {
            "H-01": {"title": "Test Vuln"},
        }
    }
    result = _find_vulnerability(config, "H-01")
    assert result["title"] == "Test Vuln"


def test_build_target_detect() -> None:
    import json

    record = _make_record()
    vuln_info = {"title": "Deposit Theft via Burn Truncation"}
    audit_config = _make_audit_config()

    target_str = _build_target(record, "detect", vuln_info, audit_config)
    target = json.loads(target_str)

    assert target["audit_id"] == "2023-07-pooltogether"
    assert target["vulnerability_id"] == "H-01"
    assert target["award_usd"] == 2181.44
    assert "findings" in target


def test_build_target_patch() -> None:
    import json

    record = _make_record()
    vuln_info = {
        "title": "Deposit Theft",
        "test": "ExploitH01.t.sol",
        "test_passes_if_vulnerable": True,
    }
    audit_config = _make_audit_config()

    target_str = _build_target(record, "patch", vuln_info, audit_config)
    target = json.loads(target_str)

    assert "test_command" in target
    assert "forge test" in target["test_command"]
    assert "ExploitH01.t.sol" in target["test_command"]


def test_build_target_exploit() -> None:
    import json

    record = _make_record()
    vuln_info = {"title": "Deposit Theft", "exploit_task": True}
    audit_config = _make_audit_config()

    target_str = _build_target(record, "exploit", vuln_info, audit_config)
    target = json.loads(target_str)

    assert target["exploit_task"] is True


def test_record_to_sample_detect(tmp_path: Any) -> None:
    """Test that record_to_sample creates a valid Sample for detect tasks."""
    # Create a mock audit directory structure
    audit_dir = tmp_path / "audits" / "2023-07-pooltogether"
    audit_dir.mkdir(parents=True)
    (audit_dir / "Dockerfile").write_text("FROM ubuntu:24.04\n")
    (audit_dir / "config.yaml").write_text(
        "id: 2023-07-pooltogether\nframework: foundry\nvulnerabilities: []\n"
    )

    record = _make_record()

    with patch("evmbench.docker.COMPOSE_FILES_DIR", tmp_path / "compose"):
        sample = _record_to_sample(record, "detect", "improved", tmp_path)

    assert sample is not None
    assert sample.id == "2023-07-pooltogether/H-01"
    assert sample.metadata is not None
    assert sample.metadata["audit_id"] == "2023-07-pooltogether"
    assert sample.metadata["award_usd"] == 2181.44
    assert sample.sandbox is not None


def test_record_to_sample_missing_audit_dir(tmp_path: Any) -> None:
    """Test that missing audit directory returns None."""
    record = _make_record()
    sample = _record_to_sample(record, "detect", "improved", tmp_path)
    assert sample is None
