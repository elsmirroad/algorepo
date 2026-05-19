import json
import os
import re
import tempfile
from pathlib import Path

from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.platforms.base import Platform
from algorepo.testers.runners.base import BaseRunner


class TypeScriptRunner(BaseRunner):
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        # 1. Get testers path
        testers_dir = platform.get_tester_dir(language_name="TypeScript")
        testers_path = testers_dir / "lc.js"

        if not testers_path.exists():
            raise TesterError(
                reason=TesterErrorReason.LIBRARY_NOT_FOUND,
                language="TypeScript",
                details=str(testers_path),
            )

        # 2. Prepare data
        test_cases, _ = self._get_test_data(description=description, platform=platform)
        tc_data = [{"inputs": tc.inputs, "expected": tc.expected} for tc in test_cases]
        test_cases_json = json.dumps(tc_data)

        testers_path_js = str(testers_path.resolve()).replace("\\", "/")

        # 3. Detect function name for auto-export
        content = filepath.read_text(encoding="utf-8")
        content_clean = re.sub(r"^export\s+", "", content, flags=re.MULTILINE)

        func_match = re.search(r"(?:var|let|const)\s+([a-zA-Z0-9_]+)\s*=\s*function", content_clean)
        if not func_match:
            func_match = re.search(r"function\s+([a-zA-Z0-9_]+)\s*\(", content_clean)

        func_name = func_match.group(1) if func_match else ""

        # 4. Generate Wrapper
        runner_content = (
            f"const {{ ListNode, TreeNode, runTest }} = require('{testers_path_js}');\n"
            f"const solution = (function(ListNode, TreeNode) {{\n"
            f"{content_clean}\n"
            f"return typeof {func_name} !== 'undefined' ? {func_name} : "
            f"(typeof Solution !== 'undefined' ? {{ Solution }} : null);\n"
            f"}}) (ListNode, TreeNode);\n"
            f"const testCases = {test_cases_json};\n"
            f"runTest(solution, testCases);\n"
        )

        with tempfile.NamedTemporaryFile(suffix=".ts", mode="w", delete=False) as tmp:
            tmp.write(runner_content)
            tmp_path = tmp.name

        try:
            # Use --yes to skip interactive installation prompt in npx
            try:
                self._execute(["npx", "--yes", "tsx", tmp_path])
            except Exception:
                self._execute(["npx", "--yes", "ts-node", tmp_path])
        except Exception as e:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="TypeScript",
                details=str(e),
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
