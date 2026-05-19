import re
import tempfile
from pathlib import Path

from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.platforms.base import Platform
from algorepo.testers.runners.base import BaseRunner


class GoRunner(BaseRunner):
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        # 1. Prepare data and signature
        test_cases, _ = self._get_test_data(description=description, platform=platform)
        sig = self._get_signature(
            filepath=filepath,
            description=description,
            language="Go",
        )

        if not sig:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="Go",
                details="Could not find Go function signature.",
            )

        method_name = sig.name
        # Build map of arg names for easier access if needed
        # Go uses name type, name type

        # 2. Generate Runner Source
        test_blocks = []
        for i, tc in enumerate(test_cases):
            call_args = []
            for j, val in enumerate(tc.inputs):
                # Basic cleanup for Go literal
                # Try to detect if it's an array based on signature if available
                arg_type = sig.args[j][1] if j < len(sig.args) else ""
                go_val = val
                if "[]" in arg_type:
                    go_val = val.replace("[", f"{arg_type}{{").replace("]", "}")
                call_args.append(go_val)

            expected_go = tc.expected
            if "[]" in sig.return_type:
                expected_go = tc.expected.replace("[", f"{sig.return_type}{{").replace("]", "}")

            block = f"""
    {{
        result := {method_name}({", ".join(call_args)})
        expected := {expected_go}
        passed := reflect.DeepEqual(result, expected)
        args := `{tc.inputs}`
        res := fmt.Sprintf("%v", result)
        exp := fmt.Sprintf("%v", expected)
        PrintStatus(passed, {i + 1}, args, res, exp)
        if !passed {{ exitCode = 1 }}
    }}"""
            test_blocks.append(block)

        # 3. Assemble full file
        solution_code = filepath.read_text(encoding="utf-8")
        # Remove potential package declaration
        solution_code = re.sub(r"package\s+[a-zA-Z0-9_]+", "", solution_code, count=1)

        runner_content = f"""
package main

import (
	"fmt"
	"reflect"
    "os"
)

// Helpers and Structures
type ListNode struct {{
	Val  int
	Next *ListNode
}}

type TreeNode struct {{
	Val   int
	Left  *TreeNode
	Right *TreeNode
}}

func PrintStatus(passed bool, id int, args string, res string, exp string) {{
	status := "\\033[91mFAILED\\033[0m"
	if passed {{
		status = "\\033[92mPASSED\\033[0m"
	}}
	fmt.Printf("%s Test %d: args %s result %s expected %s\\n", status, id, args, res, exp)
}}

// User Solution
{solution_code}

func main() {{
    exitCode := 0
    {"".join(test_blocks)}
    os.Exit(exitCode)
}}
"""
        with tempfile.NamedTemporaryFile(suffix=".go", mode="w", delete=False) as tmp:
            tmp.write(runner_content)
            tmp_path = Path(tmp.name)

        try:
            self._execute(["go", "run", str(tmp_path)])
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
