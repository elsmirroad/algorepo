import subprocess
import tempfile
from pathlib import Path

from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.platforms.base import Platform
from algorepo.testers.runners.base import BaseRunner


class CSharpRunner(BaseRunner):
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        # 1. Prepare data and signature
        test_cases, json_path = self._get_test_data(description=description, platform=platform)
        sig = self._get_signature(
            filepath=filepath,
            description=description,
            language="C#",
        )

        if not sig:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="C#",
                details="Could not find C# function signature.",
            )

        # 2. Prepare workspace
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)

            # Detect dotnet version to set TargetFramework
            target_framework = "net8.0"
            try:
                version_out = subprocess.check_output(["dotnet", "--version"], text=True).strip()
                major_version = version_out.split(".")[0]
                target_framework = f"net{major_version}.0"
            except Exception:
                pass

            # Create project file
            # RollForward=Major allows running on newer runtimes if the exact one is missing
            csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>{target_framework}</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <RollForward>Major</RollForward>
  </PropertyGroup>
</Project>
"""
            (tmp_dir_path / "Runner.csproj").write_text(csproj_content, encoding="utf-8")

            # Read solution code
            solution_code = filepath.read_text(encoding="utf-8")

            # 3. Generate Program.cs with Reflection and JSON Parsing
            program_cs = self._generate_program_cs(sig, json_path, solution_code)
            (tmp_dir_path / "Program.cs").write_text(program_cs, encoding="utf-8")

            try:
                # Run project
                # --nologo to keep output clean
                self._execute(
                    ["dotnet", "run", "--project", str(tmp_dir_path), "--nologo"], cwd=tmp_dir_path
                )
            except subprocess.CalledProcessError as e:
                # dotnet run might return non-zero if tests fail, which is handled by exitCode in C#
                # but if it fails to compile/start, it's an error.
                if e.returncode not in (1, 150):
                    # 1 is our test failure, 150 is often runtime mismatch
                    raise TesterError(
                        reason=TesterErrorReason.COMPILATION_FAILED,
                        language="C#",
                        details=e.stderr.decode() if e.stderr else str(e),
                    )
            except FileNotFoundError:
                raise TesterError(
                    reason=TesterErrorReason.RUNTIME_ERROR,
                    language="C#",
                    details="dotnet SDK not found.",
                )

    def _generate_program_cs(self, sig, json_path, solution_code):
        # Escape backslashes for C# string literal
        safe_json_path = str(json_path).replace("\\", "\\\\")

        # Breaking down long lines and removing whitespace in empty lines to satisfy ruff
        return f"""
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.Json;

// LeetCode Structures
public class ListNode {{
    public int val;
    public ListNode? next;
    public ListNode(int x) {{ val = x; }}
}}

public class TreeNode {{
    public int val;
    public TreeNode? left;
    public TreeNode? right;
    public TreeNode(int x) {{ val = x; }}
}}

// User Solution
{solution_code}

class Runner {{
    static void Main() {{
        string jsonPath = "{safe_json_path}";
        var json = File.ReadAllText(jsonPath);
        var options = new JsonSerializerOptions {{ PropertyNameCaseInsensitive = true }};
        var testCases = JsonSerializer.Deserialize<List<TestCase>>(json, options);

        if (testCases == null) return;

        var solution = new Solution();
        var flags = BindingFlags.Public | BindingFlags.Instance |
                    BindingFlags.Static | BindingFlags.IgnoreCase;
        var method = typeof(Solution).GetMethod("{sig.name}", flags);

        if (method == null) {{
            Console.WriteLine("Error: Method {sig.name} not found in Solution class.");
            Environment.Exit(1);
        }}

        int exitCode = 0;
        for (int i = 0; i < testCases.Count; i++) {{
            var tc = testCases[i];
            try {{
                var parameters = method.GetParameters();
                object?[] args = new object[parameters.Length];
                for (int j = 0; j < parameters.Length; j++) {{
                    // Convert JSON string to the expected type
                    var type = parameters[j].ParameterType;
                    args[j] = JsonSerializer.Deserialize(tc.Inputs[j], type, options);
                }}

                var result = method.Invoke(solution, args);
                var expected = JsonSerializer.Deserialize(tc.Expected, method.ReturnType, options);

                string resultJson = JsonSerializer.Serialize(result);
                string expectedJson = JsonSerializer.Serialize(expected);

                bool passed = resultJson == expectedJson;

                string status = passed
                    ? "\\u001b[92mPASSED\\u001b[0m"
                    : "\\u001b[91mFAILED\\u001b[0m";
                string argsStr = string.Join(", ", tc.Inputs);
                Console.WriteLine($"{{status}} Test {{i + 1}}: args {{argsStr}} " +
                                  $"result {{resultJson}} expected {{tc.Expected}}");

                if (!passed) exitCode = 1;
            }} catch (Exception ex) {{
                Console.WriteLine($"\\u001b[91mERROR\\u001b[0m Test {{i + 1}}: {{ex.Message}}");
                if (ex.InnerException != null)
                    Console.WriteLine($"Inner: {{ex.InnerException.Message}}");
                exitCode = 1;
            }}
        }}
        Environment.Exit(exitCode);
    }}

    private class TestCase {{
        public List<string> Inputs {{ get; set; }} = new();
        public string Expected {{ get; set; }} = "";
    }}
}}
"""
