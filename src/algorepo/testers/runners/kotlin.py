import subprocess
import tempfile
from pathlib import Path

from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.platforms.base import Platform
from algorepo.testers.runners.base import BaseRunner


class KotlinRunner(BaseRunner):
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        # 1. Prepare data and signature
        test_cases, _ = self._get_test_data(description=description, platform=platform)
        sig = self._get_signature(
            filepath=filepath,
            description=description,
            language="Kotlin",
        )

        if not sig:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="Kotlin",
                details="Could not find Kotlin function signature.",
            )

        method_name = sig.name

        def norm_type(t: str) -> str:
            return t.replace("string", "String")

        # 2. Generate Runner Source
        test_blocks = []
        for i, tc in enumerate(test_cases):
            # Kotlin conversion
            call_args = []
            for j, val in enumerate(tc.inputs):
                arg_type = norm_type(sig.args[j][1] if j < len(sig.args) else "")
                if '"' in val:
                    k_val = val.strip()
                elif "[" in val:
                    # Map to Kotlin array creation
                    prefix = "intArrayOf" if "IntArray" in arg_type else "arrayOf"
                    k_val = val.replace("[", f"{prefix}(").replace("]", ")")
                else:
                    k_val = val
                call_args.append(k_val)

            ret_type = norm_type(sig.return_type)
            if '"' in tc.expected:
                expected_k = tc.expected.strip()
            elif "[" in tc.expected:
                prefix = "intArrayOf" if "IntArray" in ret_type else "arrayOf"
                expected_k = tc.expected.replace("[", f"{prefix}(").replace("]", ")")
            else:
                expected_k = tc.expected

            inputs_escaped = str(tc.inputs).replace('"', '\\"')
            expected_escaped = tc.expected.replace('"', '\\"')

            block = f"""
    val result{i} = sol.{method_name}({", ".join(call_args)})
    val expected{i} = {expected_k}
    val ok{i} = Objects.deepEquals(result{i}, expected{i})

    val resStr{i} = if (result{i} is IntArray) Arrays.toString(result{i})
                 else if (result{i} is Array<*>) Arrays.deepToString(result{i} as Array<*>)
                 else result{i}.toString()

    printStatus(ok{i}, {i + 1}, "{inputs_escaped}", resStr{i}, "{expected_escaped}")
    if (!ok{i}) exitCode = 1
"""
            test_blocks.append(block)

        solution_code = filepath.read_text(encoding="utf-8")

        runner_content = f"""
import java.util.*

class ListNode(var `val`: Int) {{ var next: ListNode? = null }}
class TreeNode(var `val`: Int) {{
    var left: TreeNode? = null; var right: TreeNode? = null
}}

fun printStatus(passed: Boolean, id: Int, args: String, res: String, exp: String) {{
    val status = if (passed) "\\u001B[92mPASSED\\u001B[0m" else "\\u001B[91mFAILED\\u001B[0m"
    println("$status Test $id: args $args result $res expected $exp")
}}

{solution_code}

fun main(args: Array<String>) {{
    val sol = Solution()
    var exitCode = 0
    {"".join(test_blocks)}
    System.exit(exitCode)
}}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_dir_path = Path(tmpdir)
            runner_kt = tmp_dir_path / "Runner.kt"
            runner_kt.write_text(runner_content, encoding="utf-8")

            try:
                # Compile
                res = subprocess.run(
                    [
                        "kotlinc",
                        str(runner_kt),
                        "-include-runtime",
                        "-d",
                        str(tmp_dir_path / "Runner.jar"),
                    ],
                    capture_output=True,
                    text=True,
                )
                if res.returncode != 0:
                    raise TesterError(
                        reason=TesterErrorReason.COMPILATION_FAILED,
                        language="Kotlin",
                        details=res.stderr,
                    )

                # Run
                self._execute(["java", "-cp", str(tmp_dir_path / "Runner.jar"), "RunnerKt"])
            except subprocess.CalledProcessError as e:
                err_msg = e.stderr.decode() if hasattr(e.stderr, "decode") else str(e)
                raise TesterError(
                    reason=TesterErrorReason.RUNTIME_ERROR,
                    language="Kotlin",
                    details=err_msg,
                )
            except FileNotFoundError:
                raise TesterError(
                    reason=TesterErrorReason.RUNTIME_ERROR,
                    language="Kotlin",
                    details="kotlinc or java not found.",
                )
