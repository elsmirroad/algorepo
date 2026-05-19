import subprocess
import tempfile
from pathlib import Path

from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.platforms.base import Platform
from algorepo.testers.runners.base import BaseRunner
from algorepo.utils.workspace import get_binary_path


class RustRunner(BaseRunner):
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        # 1. Prepare data and signature
        test_cases, _ = self._get_test_data(description=description, platform=platform)
        sig = self._get_signature(
            filepath=filepath,
            description=description,
            language="Rust",
        )

        if not sig:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="Rust",
                details="Could not find Rust function signature.",
            )

        method_name = sig.name

        # 2. Generate Runner Source
        test_blocks = []
        for i, tc in enumerate(test_cases):
            # Basic Rust conversion with better escaping
            call_args = []
            for val in tc.inputs:
                # Handle strings and vectors
                rust_val = val.replace("[", "vec![").replace("]", "]")
                # If it looks like a string in Rust signature, wrap it
                if '"' in val:
                    rust_val = f"String::from({val})"
                call_args.append(rust_val)

            expected_rust = tc.expected.replace("[", "vec![").replace("]", "]")
            if '"' in tc.expected:
                expected_rust = f"String::from({tc.expected})"

            inputs_escaped = str(tc.inputs).replace('"', '\\"')

            block = f"""
    {{
        let result = Solution::{method_name}({", ".join(call_args)});
        let expected = {expected_rust};
        let passed = result == expected;
        println!("{{}} Test {i + 1}: args {{:?}} result {{:?}} expected {{:?}}",
                 if passed {{ "\\x1b[92mPASSED\\x1b[0m" }} else {{ "\\x1b[91mFAILED\\x1b[0m" }},
                 "{inputs_escaped}", result, expected);
        if !passed {{ exit_code = 1; }}
    }}"""
            test_blocks.append(block)

        solution_code = filepath.read_text(encoding="utf-8")
        if "struct Solution" not in solution_code:
            struct_def = "struct Solution;"
        else:
            struct_def = ""

        runner_content = f"""
{struct_def}

{solution_code}

fn main() {{
    let mut exit_code = 0;
    {"".join(test_blocks)}
    std::process::exit(exit_code);
}}
"""

        with tempfile.NamedTemporaryFile(suffix=".rs", mode="w", delete=False) as tmp:
            tmp.write(runner_content)
            tmp_path = Path(tmp.name)

        try:
            exe_path = tmp_path.with_suffix(".out")
            rustc_path = get_binary_path("rustc")

            if not rustc_path:
                raise TesterError(
                    reason=TesterErrorReason.RUNTIME_ERROR,
                    language="Rust",
                    details="rustc not found.",
                )

            result = subprocess.run(
                [str(rustc_path), str(tmp_path), "-o", str(exe_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise TesterError(
                    reason=TesterErrorReason.COMPILATION_FAILED,
                    language="Rust",
                    details=result.stderr,
                )

            self._execute([str(exe_path)])
            if exe_path.exists():
                exe_path.unlink()
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
