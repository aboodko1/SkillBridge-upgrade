"""Phase 2 data-truth/language — frontend source-contract guard.

Covers: canonical metric keys in the type layer, backend-sourced target
coverage (no browser recomputation), distinctly labelled catalogue similarity,
labelled stale paths, and a gap-aware completion claim.
"""

import shutil
import subprocess

import pytest

from contract_paths import WORKSPACE_ROOT, checker_script, node_env


def test_runtime_data_truth_phase2_frontend_contracts_hold():
    node = shutil.which("node")
    if not node:
        pytest.skip("node is required to run SkillBridge but was not found")
    script = checker_script("check-data-truth-phase2.mjs")
    assert script.exists()
    result = subprocess.run([node, str(script)], cwd=WORKSPACE_ROOT, capture_output=True,
                            text=True, timeout=120, env=node_env())
    assert result.returncode == 0, (
        f"Data truth (Phase 2) frontend contracts broken:\n"
        f"{result.stdout}\n{result.stderr}")
