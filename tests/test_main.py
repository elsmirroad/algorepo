
import pytest
from pydantic import HttpUrl

from algorepo.config import Config
from algorepo.exceptions import ConfigurationError, SolutionsListError
from algorepo.languages import Language
from algorepo.main import Algorepo, DownloadResult
from algorepo.models import Problem
from algorepo.platforms.base import Platform


@pytest.fixture
def mock_config(tmp_path):
    return Config(
        solutions_dir=tmp_path / "Solutions",
        language_priority=["Python3"],
        editor="nvim",
    )


@pytest.fixture
def mock_algorepo(mocker, mock_config):
    mocker.patch("algorepo.main.Config.from_yaml", return_value=mock_config)
    return Algorepo()


def test_algorepo_get_filename(mock_algorepo):
    assert mock_algorepo.get_filename("leetcode", "1", "Two Sum") == "1. Two Sum"
    assert mock_algorepo.get_filename("codewars", "123", "Even or Odd") == "Even or Odd | 123"
    assert mock_algorepo.get_filename("unknown", "1", "Some Problem") == "Some Problem"


def test_algorepo_open_in_editor_success(mocker, mock_algorepo, tmp_path):
    file_path = tmp_path / "file.py"
    mock_run = mocker.patch("subprocess.run")
    mock_algorepo.open_in_editor(file_path)
    mock_run.assert_called_once_with(["nvim", str(file_path)])


def test_algorepo_open_in_editor_not_found(mocker, mock_algorepo, tmp_path):
    file_path = tmp_path / "file.py"
    mocker.patch("subprocess.run", side_effect=FileNotFoundError)
    with pytest.raises(ConfigurationError) as exc:
        mock_algorepo.open_in_editor(file_path)
    assert "Failed to open editor 'nvim'" in str(exc.value)


def test_algorepo_open_in_editor_permission_error(mocker, mock_algorepo, tmp_path):
    file_path = tmp_path / "file.py"
    mocker.patch("subprocess.run", side_effect=PermissionError)
    with pytest.raises(ConfigurationError) as exc:
        mock_algorepo.open_in_editor(file_path)
    assert "cannot open editor" in str(exc.value)


def test_algorepo_get_info_empty_dir(mock_algorepo):
    with pytest.raises(SolutionsListError) as exc:
        mock_algorepo.get_info()
    assert "Solutions directory not found" in str(exc.value)


def test_algorepo_get_info_success(mock_algorepo, tmp_path):
    solutions_dir = tmp_path / "Solutions"
    leetcode_dir = solutions_dir / "LeetCode"
    leetcode_dir.mkdir(parents=True)
    (leetcode_dir / "1. Two Sum.py").touch()

    info = mock_algorepo.get_info()
    assert "LeetCode" in info
    assert info["LeetCode"] == ["1. Two Sum.py"]

    info_platform = mock_algorepo.get_info(platform="leetcode")
    assert "LeetCode" in info_platform
    assert info_platform["LeetCode"] == ["1. Two Sum.py"]


def test_algorepo_download_problem(mocker, mock_algorepo, tmp_path):
    url = "https://leetcode.com/problems/two-sum/"

    problem = Problem(
        problem_id="1",
        title="Two Sum",
        difficulty="Easy",
        platform="leetcode",
        description="description",
        url=HttpUrl(url),
        available_languages=["python"],
        code_snippets={"python": "def twoSum(): pass"},
    )

    lang = Language(
        name="Python3",
        extension=".py",
        platform_ids={"leetcode": "python"},
        comment_symbol="#",
        tester={}
    )

    class MockPlatform(Platform):
        def fetch(self, url: str) -> dict: return {}
        def parse(self, raw: dict, url: str) -> Problem: return problem

    mocker.patch("algorepo.main.validate_url", return_value="leetcode")
    mocker.patch("algorepo.main.get_platform", return_value=MockPlatform(mock_algorepo.config))
    mocker.patch("algorepo.main.select_language", return_value=lang)
    mocker.patch("algorepo.main.render_solution_file", return_value="# Code here")
    mocker.patch("os.chdir")

    result = mock_algorepo.download_problem(url)

    assert isinstance(result, DownloadResult)
    assert result.problem == problem
    assert result.language == lang

    assert result.filepath.exists()
    assert result.filepath.name == "1. Two Sum.py"
    assert result.filepath.read_text() == "# Code here"
