import subprocess
import tempfile
from pathlib import Path

from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.platforms.base import Platform
from algorepo.testers.runners.base import BaseRunner
from algorepo.utils.tester import to_cpp_literal
from algorepo.utils.workspace import get_binary_path


class CPPRunner(BaseRunner):
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        # 1. Prepare data and signature
        test_cases, _ = self._get_test_data(description=description, platform=platform)
        sig = self._get_signature(filepath=filepath, description=description, language="C++")

        if not sig:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="C++",
                details="Could not find CPP function signature.",
            )

        method_name = sig.name
        res_type = sig.return_type

        # 2. Get testers path
        testers_path = platform.get_tester_dir(language_name="C++")
        if not (testers_path / "lc.hpp").exists():
            raise TesterError(
                reason=TesterErrorReason.LIBRARY_NOT_FOUND,
                language="C++",
                details=str(testers_path / "lc.hpp"),
            )

        # 3. Generate Runner Source
        test_blocks = []
        for i, tc in enumerate(test_cases):
            inits = []
            call_args = []
            for j, val in enumerate(tc.inputs):
                arg_name, arg_type = sig.args[j] if j < len(sig.args) else (f"arg{j}", "")
                cpp_val = to_cpp_literal(val)
                inits.append(f"        {arg_type} {arg_name} = {cpp_val};")
                call_args.append(arg_name)

            expected_cpp = to_cpp_literal(tc.expected)
            inputs_escaped = str(tc.inputs).replace('"', '\\"')

            block = f"""
    {{
{chr(10).join(inits)}
        {res_type} expected = {expected_cpp};
        {res_type} result = sol.{method_name}({", ".join(call_args)});
        bool ok = (result == expected);
        lc::print_status(ok, {i + 1}, "{inputs_escaped}",
                         lc::to_str(result), lc::to_str(expected));
        if (!ok) exit_code = 1;
    }}"""
            test_blocks.append(block)

        runner_content = f"""
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include "{testers_path / "lc.hpp"}"

using namespace std;

// Include user solution
#include "{filepath.resolve()}"

int main() {{
    Solution sol;
    int exit_code = 0;
    {"".join(test_blocks)}
    return exit_code;
}}
"""

        # 4. Compile and Run
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_dir_path = Path(tmpdir)
            runner_cpp = tmp_dir_path / "runner.cpp"
            runner_cpp.write_text(runner_content, encoding="utf-8")
            exe_path = tmp_dir_path / "runner.exe"

            gpp_path = get_binary_path("g++")
            if not gpp_path:
                raise TesterError(
                    reason=TesterErrorReason.RUNTIME_ERROR,
                    language="C++",
                    details="g++ not found.",
                )

            compile_cmd = [
                str(gpp_path),
                "-std=c++17",
                str(runner_cpp),
                "-o",
                str(exe_path),
                f"-I{testers_path}",
            ]
            try:
                subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
                self._execute([str(exe_path)])
            except subprocess.CalledProcessError as e:
                raise TesterError(
                    reason=TesterErrorReason.COMPILATION_FAILED,
                    language="C++",
                    details=e.stderr,
                )
            except FileNotFoundError:
                raise TesterError(
                    reason=TesterErrorReason.RUNTIME_ERROR,
                    language="C++",
                    details="g++ not found.",
                )
