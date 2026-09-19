"""Learning Phase 3 agentic frontend source-contract guard.

Pins the learning-agent UI to the real orchestrator API: the decision and its
evidence are rendered, practice/Mini Check go through the real lesson APIs, a
non-executing static check is labelled honestly, the English/Egyptian-Arabic
learning language choice persists, errors offer a retry, and the full roadmap
stays reachable.
"""

import shutil
import subprocess

import pytest

from contract_paths import WORKSPACE_ROOT, checker_script, node_env


def test_runtime_learning_phase3_agentic_frontend_contracts_hold():
    node = shutil.which("node")
    if not node:
        pytest.skip("node is required to run SkillBridge but was not found")
    script = checker_script("check-learning-phase3-agentic.mjs")
    assert script.exists()
    result = subprocess.run([node, str(script)], cwd=WORKSPACE_ROOT, capture_output=True,
                            text=True, timeout=120, env=node_env())
    assert result.returncode == 0, (
        f"Learning Phase 3 agentic frontend contracts broken:\n{result.stdout}\n{result.stderr}")
