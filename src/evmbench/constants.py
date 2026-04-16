"""Constants for the EVMbench evaluation."""

from pathlib import Path
from typing import Literal

EVMBENCH_REPO = "openai/frontier-evals"
EVMBENCH_COMMIT_SHA = "8ea5c659b5232d3c520c5ca2a018fe65dc5e1988"
EVMBENCH_SUBDIR = "project/evmbench"

CACHE_DIR = Path.home() / ".cache" / "inspect_evals" / "evmbench"
COMPOSE_FILES_DIR = CACHE_DIR / "compose_files"

# Workspace paths matching reference implementation
AGENT_DIR = "/home/agent"
AUDIT_DIR = "/home/agent/audit"
SUBMISSION_DIR = "/home/agent/submission"
LOGS_DIR = "/home/logs"

# Exploit wallet configuration (from reference constants.py)
EXPLOIT_WALLET_ADDRESS = "FCAd0B19bB29D4674531d6f115237E16AfCE377c"
EXPLOIT_WALLET_PRIVATE_KEY = (
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)
EXPLOIT_CHAIN_ID = 31337
EXPLOIT_RPC_PORT = 8545

# Blocked RPC methods for veto proxy (prevents agent cheating)
BLOCKED_RPC_METHODS = [
    "eth_sendRawTransaction",
    "eth_sendTransaction",
    "eth_accounts",
    "eth_getAccount",
    "eth_setCode",
    "eth_setBalance",
    "eth_setStorage",
    "eth_sign",
    "eth_signTransaction",
    "eth_signTypedData",
    "evm_mine",
    "evm_addAccount",
    "evm_setAutomine",
    "evm_setIntervalMining",
    "evm_setBlockGasLimit",
    "evm_setNextBlockTimestamp",
    "evm_snapshot",
    "evm_revert",
    "evm_increaseTime",
    "hardhat_setBalance",
    "hardhat_setCode",
    "hardhat_setNonce",
    "hardhat_setStorageAt",
    "hardhat_impersonateAccount",
    "hardhat_stopImpersonatingAccount",
    "hardhat_mine",
    "hardhat_reset",
    "personal_sign",
    "personal_sendTransaction",
    "personal_unlockAccount",
    "personal_importRawKey",
]

TaskType = Literal["detect", "patch", "exploit"]

# Default limits
DEFAULT_MESSAGE_LIMIT = 200
DEFAULT_TIME_LIMIT_HOURS = 1.0
PAPER_TIME_LIMIT_HOURS = 6.0
