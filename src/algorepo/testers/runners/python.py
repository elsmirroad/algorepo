import importlib.util
import sys
from pathlib import Path

from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.platforms.base import Platform
from algorepo.testers.runners.base import BaseRunner


class PythonRunner(BaseRunner):
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        # 1. Prepare data
        test_cases, _ = self._get_test_data(description=description, platform=platform)

        # 2. Get testers path
        testers_dir = platform.get_tester_dir(language_name="Python")
        testers_path = testers_dir / "lc.py"

        if not testers_path.exists():
            raise TesterError(
                reason=TesterErrorReason.LIBRARY_NOT_FOUND,
                language="Python",
                details=str(testers_path),
            )

        # 3. Load the tester library (lc.py)
        spec = importlib.util.spec_from_file_location("lc", testers_path)
        if spec and spec.loader:
            lc = importlib.util.module_from_spec(spec)
            sys.modules["lc"] = lc
            spec.loader.exec_module(lc)
        else:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="Python",
                details="Failed to load lc.py",
            )

        # 4. Load the user's solution
        spec = importlib.util.spec_from_file_location("solution", filepath)
        if spec and spec.loader:
            solution_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(solution_mod)
        else:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="Python",
                details=f"Failed to load solution from {filepath}",
            )

        # 5. Run tests using the helper in lc.py
        # Find Solution class or standalone function
        solution_obj = getattr(solution_mod, "Solution", None)
        if not solution_obj:
            # Try to find any function in the module
            funcs = [
                getattr(solution_mod, name)
                for name in dir(solution_mod)
                if callable(getattr(solution_mod, name)) and not name.startswith("__")
            ]
            if funcs:
                solution_obj = funcs[0]

        if solution_obj:
            # We need to adapt TestCase objects to what lc.test expects
            # lc.test expects a list of dicts or a raw string description
            # But we can call its internal run_test if available or just use the logic
            lc.run_test(solution_obj, test_cases)
        else:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="Python",
                details="No Solution class or function found in the file.",
            )
