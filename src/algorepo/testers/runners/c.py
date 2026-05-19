import subprocess
import tempfile
from pathlib import Path

from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.platforms.base import Platform
from algorepo.testers.runners.base import BaseRunner
from algorepo.utils.tester import to_c_literal
from algorepo.utils.workspace import get_binary_path


class CRunner(BaseRunner):
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        # 1. Prepare data and signature
        test_cases, _ = self._get_test_data(description=description, platform=platform)
        sig = self._get_signature(filepath=filepath, description=description, language="C")

        if not sig:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="C",
                details="Could not find C function signature.",
            )

        method_name = sig.name
        res_type = sig.return_type

        # 2. Get testers path
        testers_path = platform.get_tester_dir(language_name="C") / "lc.h"
        if not testers_path.exists():
            raise TesterError(
                reason=TesterErrorReason.LIBRARY_NOT_FOUND,
                language="C",
                details=str(testers_path),
            )

        # 3. Generate Runner Source
        test_blocks = []
        for i, tc in enumerate(test_cases):
            call_args = []
            for j, val in enumerate(tc.inputs):
                arg_type = sig.args[j][1] if j < len(sig.args) else ""
                c_val = to_c_literal(val, arg_type)
                call_args.append(c_val)

            clean_expected = to_c_literal(tc.expected, res_type)
            res_c_type = res_type.replace("string", "char*")

            # Simple check for result comparison
            if "char*" in res_c_type or "char *" in res_c_type:
                comp = f"strcmp(result, {clean_expected}) == 0"
            else:
                comp = f"result == {clean_expected}"

            inputs_escaped = str(tc.inputs).replace('"', '\\"')
            expected_escaped = tc.expected.replace('"', '\\"').strip()

            block = f"""
    {{
        {res_c_type} result = {method_name}({", ".join(call_args)});
        int passed = {comp};
        print_status(passed, {i + 1}, "{inputs_escaped}", "", "{expected_escaped}");
        if (!passed) exit_code = 1;
    }}"""
            test_blocks.append(block)

        solution_code = filepath.read_text(encoding="utf-8")
        runner_content = f"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "{testers_path.resolve()}"

{solution_code}

int main() {{
    int exit_code = 0;
    {"".join(test_blocks)}
    return exit_code;
}}
"""
        with tempfile.NamedTemporaryFile(suffix=".c", mode="w", delete=False) as tmp:
            tmp.write(runner_content)
            tmp_path = Path(tmp.name)

        try:
            exe_path = tmp_path.with_suffix(".out")
            gcc_path = get_binary_path("gcc")
            if not gcc_path:
                raise TesterError(
                    reason=TesterErrorReason.RUNTIME_ERROR,
                    language="C",
                    details="gcc not found.",
                )

            compile_cmd = [str(gcc_path), str(tmp_path), "-o", str(exe_path), "-lm"]

            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise TesterError(
                    reason=TesterErrorReason.COMPILATION_FAILED,
                    language="C",
                    details=result.stderr,
                )

            self._execute([str(exe_path)])
            if exe_path.exists():
                exe_path.unlink()
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
