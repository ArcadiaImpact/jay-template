"""Docker infrastructure for EVMbench per-sample sandbox environments.

Generates per-sample compose.yaml files that reference the audit-specific
Dockerfiles from the EVMbench reference implementation.
"""

import logging
import subprocess
from pathlib import Path

from inspect_ai.util import SandboxEnvironmentSpec

from evmbench.constants import COMPOSE_FILES_DIR, EXPLOIT_CHAIN_ID, EXPLOIT_RPC_PORT

logger = logging.getLogger(__name__)


def get_sandbox_spec(
    audit_id: str,
    task_type: str,
    data_dir: Path,
) -> SandboxEnvironmentSpec:
    """Generate a per-sample Docker sandbox spec.

    Creates a compose.yaml that builds from the audit's Dockerfile.
    For exploit tasks, includes an Anvil service for the local testnet.

    Args:
        audit_id: The audit identifier (e.g., "2023-07-pooltogether").
        task_type: One of "detect", "patch", "exploit".
        data_dir: Path to the extracted EVMbench data directory.

    Returns:
        A SandboxEnvironmentSpec pointing to the generated compose file.
    """
    compose_path = _get_compose_file(audit_id, task_type, data_dir)
    return SandboxEnvironmentSpec(type="docker", config=str(compose_path))


def _get_compose_file(
    audit_id: str,
    task_type: str,
    data_dir: Path,
) -> Path:
    """Generate a per-sample compose.yaml file.

    Args:
        audit_id: The audit identifier.
        task_type: One of "detect", "patch", "exploit".
        data_dir: Path to the extracted EVMbench data directory.

    Returns:
        Path to the generated compose.yaml file.
    """
    audit_dir = data_dir / "audits" / audit_id
    compose_dir = COMPOSE_FILES_DIR / audit_id
    compose_dir.mkdir(parents=True, exist_ok=True)
    compose_path = compose_dir / f"{task_type}-compose.yaml"

    build_context = str(audit_dir.resolve())

    if task_type == "exploit":
        content = _exploit_compose(build_context)
    else:
        content = _standard_compose(build_context)

    compose_path.write_text(content)
    return compose_path


def _standard_compose(build_context: str) -> str:
    """Compose file for detect and patch tasks (single container)."""
    return f"""\
services:
  default:
    build:
      context: {build_context}
      dockerfile: Dockerfile
    init: true
    command: tail -f /dev/null
"""


def _exploit_compose(build_context: str) -> str:
    """Compose file for exploit tasks (container + Anvil testnet)."""
    return f"""\
services:
  default:
    build:
      context: {build_context}
      dockerfile: Dockerfile
    init: true
    command: tail -f /dev/null
    depends_on:
      anvil:
        condition: service_started
  anvil:
    image: evmbench/base:latest
    x-local: true
    command: >-
      anvil
      --host 0.0.0.0
      --port {EXPLOIT_RPC_PORT}
      --chain-id {EXPLOIT_CHAIN_ID}
      --accounts 10
      --balance 10000
    expose:
      - "{EXPLOIT_RPC_PORT}"
"""


def ensure_base_images(data_dir: Path) -> None:
    """Build EVMbench base Docker images if they don't exist locally.

    Build order:
    1. ploit-builder:latest — Rust binaries (ploit + veto CLI)
    2. evmbench/base:latest — Ubuntu base with Foundry, Node, and tooling

    Per-audit images (step 3) are built automatically by Inspect's Docker
    sandbox from the generated compose files.
    """
    if _image_exists("evmbench/base:latest"):
        return

    if not _image_exists("ploit-builder:latest"):
        logger.info(
            "Building ploit-builder:latest (Rust compile — may take several minutes)"
        )
        subprocess.run(
            [
                "docker", "build",
                "-t", "ploit-builder:latest",
                "--target", "ploit-builder",
                "-f", "ploit/Dockerfile",
                ".",
            ],
            cwd=data_dir,
            check=True,
        )

    logger.info("Building evmbench/base:latest")
    subprocess.run(
        [
            "docker", "build",
            "-t", "evmbench/base:latest",
            ".",
        ],
        cwd=data_dir / "evmbench",
        check=True,
    )


def _image_exists(tag: str) -> bool:
    """Check if a Docker image exists locally."""
    result = subprocess.run(
        ["docker", "image", "inspect", tag],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0
