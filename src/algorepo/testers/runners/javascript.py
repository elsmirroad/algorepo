import json
import os
import re
import tempfile
from pathlib import Path

from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.platforms.base import Platform
from algorepo.testers.runners.base import BaseRunner


class JavaScriptRunner(BaseRunner):
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        # 1. Get testers path
        testers_dir = platform.get_tester_dir(language_name="JavaScript")
        testers_path = testers_dir / "lc.js"

        if not testers_path.exists():
            raise TesterError(
                reason=TesterErrorReason.LIBRARY_NOT_FOUND,
                language="JavaScript",
                details=str(testers_path),
            )

        # 2. Prepare data
        test_cases, _ = self._get_test_data(description=description, platform=platform)
        test_cases_json = json.dumps(
            [{"inputs": tc.inputs, "expected": tc.expected} for tc in test_cases]
        )

        testers_path_js = str(testers_path.resolve()).replace("\\", "/")

        # 3. Detect function name for auto-export
        content = filepath.read_text(encoding="utf-8")
        func_match = re.search(r"(?:var|let|const)\s+([a-zA-Z0-9_]+)\s*=\s*function", content)
        if not func_match:
            func_match = re.search(r"function\s+([a-zA-Z0-9_]+)\s*\(", content)

        func_name = func_match.group(1) if func_match else ""

        # 4. Generate Wrapper
        runner_content = (
            f"const {{ ListNode, TreeNode, runTest }} = require('{testers_path_js}');\n"
            f"const solution = (function(ListNode, TreeNode) {{\n"
            f"{content}\n"
            f"return typeof {func_name} !== 'undefined' ? {func_name} : "
            f"(typeof Solution !== 'undefined' ? {{ Solution }} : null);\n"
            f"}}) (ListNode, TreeNode);\n"
            f"const testCases = {test_cases_json};\n"
            f"runTest(solution, testCases);\n"
        )

        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as tmp:
            tmp.write(runner_content)
            tmp_path = tmp.name

        try:
            self._execute(["node", tmp_path])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
