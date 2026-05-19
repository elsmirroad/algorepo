import re
import subprocess
import tempfile
from pathlib import Path

from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.platforms.base import Platform
from algorepo.testers.runners.base import BaseRunner


class JavaRunner(BaseRunner):
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        # 1. Prepare data and signature
        test_cases, _ = self._get_test_data(description=description, platform=platform)
        sig = self._get_signature(
            filepath=filepath,
            description=description,
            language="Java",
        )

        if not sig:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="Java",
                details="Could not find Java function signature.",
            )

        method_name = sig.name

        # Normalize types (e.g., string -> String)
        def norm_type(t: str) -> str:
            return t.replace("string", "String")

        res_type = norm_type(sig.return_type)

        # 2. Generate Runner Source
        test_blocks = []
        for i, tc in enumerate(test_cases):
            call_args = []
            for j, val in enumerate(tc.inputs):
                arg_type = norm_type(sig.args[j][1] if j < len(sig.args) else "")
                # Basic Java literal conversion
                j_val = (
                    val.replace("[", "new int[]{").replace("]", "}") if "[]" in arg_type else val
                )
                call_args.append(j_val)

            expected_java = (
                tc.expected.replace("[", f"new {res_type}{{").replace("]", "}")
                if "[]" in res_type
                else tc.expected
            )
            inputs_escaped = str(tc.inputs).replace('"', '\\"')
            expected_escaped = tc.expected.replace('"', '\\"')

            block = f"""
        {{
            {res_type} expected = {expected_java};
            {res_type} result = sol.{method_name}({", ".join(call_args)});
            boolean ok = Objects.deepEquals(result, expected);
            printStatus(ok, {i + 1}, "{inputs_escaped}",
                        Arrays.deepToString(new Object[]{{result}}), "{expected_escaped}");
            if (!ok) exitCode = 1;
        }}"""
            test_blocks.append(block)

        solution_code = filepath.read_text(encoding="utf-8")
        # Ensure Solution is not public to live in Runner.java
        solution_code = solution_code.replace("public class Solution", "class Solution")
        # Remove package declarations
        solution_code = re.sub(r"package\s+[a-zA-Z0-9.]+;", "", solution_code)

        runner_content = f"""
import java.util.*;

// LeetCode Structures
class ListNode {{ int val; ListNode next; ListNode(int x) {{ val = x; }} }}
class TreeNode {{
    int val; TreeNode left; TreeNode right; TreeNode(int x) {{ val = x; }}
}}

// User Solution
{solution_code}

public class Runner {{
    public static void main(String[] args) {{
        int exitCode = 0;
        Solution sol = new Solution();
        {"".join(test_blocks)}
        System.exit(exitCode);
    }}

    private static void printStatus(boolean passed, int id, String args, String res, String exp) {{
        String status = passed ? "\\033[92mPASSED\\033[0m" : "\\033[91mFAILED\\033[0m";
        System.out.printf("%s Test %d: args %s result %s expected %s\\n",
                          status, id, args, res, exp);
    }}
}}
"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)
            runner_java = tmp_dir_path / "Runner.java"
            runner_java.write_text(runner_content, encoding="utf-8")

            try:
                # Compile
                subprocess.run(["javac", str(runner_java)], check=True, capture_output=True)
                # Run
                self._execute(["java", "-cp", str(tmp_dir_path), "Runner"])
            except subprocess.CalledProcessError as e:
                raise TesterError(
                    reason=TesterErrorReason.COMPILATION_FAILED,
                    language="Java",
                    details=e.stderr.decode() if e.stderr else str(e),
                )
            except FileNotFoundError:
                raise TesterError(
                    reason=TesterErrorReason.RUNTIME_ERROR,
                    language="Java",
                    details="javac or java not found.",
                )
