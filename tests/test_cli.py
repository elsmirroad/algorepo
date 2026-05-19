from pathlib import Path

import pytest
from pydantic import HttpUrl
from typer.testing import CliRunner

from algorepo.cli import app
from algorepo.exceptions import (
    ConfigErrorReason,
    ConfigurationError,
    NetworkError,
    NetworkErrorReason,
    SolutionsListError,
)
from algorepo.languages import Language
from algorepo.main import DownloadResult
from algorepo.models import Problem

runner = CliRunner()


@pytest.fixture
def mock_algorepo_class(mocker):
    return mocker.patch("algorepo.cli.Algorepo")


def test_cli_default_command_url_fallback(mock_algorepo_class):
    """Test that passing a URL directly defaults to the download command"""
    mock_instance = mock_algorepo_class.return_value

    lang = Language(
        name="Python3",
        extension=".py",
        platform_ids={"leetcode": "python"},
        comment_symbol="#",
        tester={},
    )
    problem = Problem(
        problem_id="1",
        title="Two Sum",
        difficulty="Easy",
        platform="leetcode",
        description="",
        url=HttpUrl("https://leetcode.com/problems/two-sum/"),
        available_languages=["python"],
        code_snippets={},
    )
    mock_result = DownloadResult(
        filepath=Path("/tmp/1. Two Sum.py"), problem=problem, language=lang
    )
    mock_instance.download_problem.return_value = mock_result

    result = runner.invoke(app, ["https://leetcode.com/problems/two-sum/"])

    assert result.exit_code == 0
    mock_instance.download_problem.assert_called_once()
    assert "Two Sum" in result.stdout


def test_cli_default_command_invalid():
    """Test that passing invalid argument without http fails"""
    result = runner.invoke(app, ["invalid-command"])
    assert result.exit_code == 1


def test_cli_download_success(mock_algorepo_class):
    mock_instance = mock_algorepo_class.return_value

    lang = Language(
        name="Python3",
        extension=".py",
        platform_ids={"leetcode": "python"},
        comment_symbol="#",
        tester={},
    )
    problem = Problem(
        problem_id="1",
        title="Two Sum",
        difficulty="Easy",
        platform="leetcode",
        description="",
        url=HttpUrl("https://leetcode.com/problems/two-sum/"),
        available_languages=["python"],
        code_snippets={},
    )
    mock_result = DownloadResult(
        filepath=Path("/tmp/1. Two Sum.py"), problem=problem, language=lang
    )
    mock_instance.download_problem.return_value = mock_result

    result = runner.invoke(
        app,
        ["download", "https://leetcode.com/problems/two-sum/", "--lang", "python", "--no-editor"],
    )

    assert result.exit_code == 0
    mock_instance.download_problem.assert_called_once_with(
        url="https://leetcode.com/problems/two-sum/",
        language="python",
        open_editor=False
    )
    assert "Two Sum" in result.stdout
    mock_instance.open_in_editor.assert_not_called()


def test_cli_download_with_editor(mock_algorepo_class):
    mock_instance = mock_algorepo_class.return_value

    lang = Language(
        name="Python3",
        extension=".py",
        platform_ids={"leetcode": "python"},
        comment_symbol="#",
        tester={},
    )
    problem = Problem(
        problem_id="1",
        title="Two Sum",
        difficulty="Easy",
        platform="leetcode",
        description="",
        url=HttpUrl("https://leetcode.com/problems/two-sum/"),
        available_languages=["python"],
        code_snippets={},
    )
    mock_result = DownloadResult(
        filepath=Path("/tmp/1. Two Sum.py"), problem=problem, language=lang
    )
    mock_instance.download_problem.return_value = mock_result

    result = runner.invoke(app, ["download", "https://leetcode.com/problems/two-sum/"])

    assert result.exit_code == 0
    mock_instance.open_in_editor.assert_called_once_with(mock_result.filepath)


def test_cli_download_error(mock_algorepo_class):
    mock_instance = mock_algorepo_class.return_value
    mock_instance.download_problem.side_effect = NetworkError(
        platform_name="leetcode",
        reason=NetworkErrorReason.HTTP_ERROR,
        details="500 Server Error"
    )

    result = runner.invoke(app, ["download", "https://leetcode.com/problems/two-sum/"])

    assert result.exit_code == 1
    assert "Error:" in result.stdout
    assert "500 Server Error" in result.stdout


def test_cli_config_success(mock_algorepo_class):
    mock_instance = mock_algorepo_class.return_value
    mock_instance.config_path = Path("/tmp/config.yaml")

    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    mock_instance.open_in_editor.assert_called_once_with(Path("/tmp/config.yaml"))


def test_cli_config_error(mock_algorepo_class):
    mock_instance = mock_algorepo_class.return_value
    mock_instance.open_in_editor.side_effect = ConfigurationError(
        reason=ConfigErrorReason.EDITOR, path=None, editor="vim"
    )

    result = runner.invoke(app, ["config"])

    assert result.exit_code == 1
    assert "Error:" in result.stdout
    assert "Failed to open editor 'vim'" in result.stdout


def test_cli_list_solutions_success(mock_algorepo_class):
    mock_instance = mock_algorepo_class.return_value
    mock_instance.get_info.return_value = {"LeetCode": ["1. Two Sum.py"]}

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    mock_instance.get_info.assert_called_once_with(platform=None)
    assert "SOLUTIONS" in result.stdout
    assert "LeetCode" in result.stdout
    assert "1. Two Sum.py" in result.stdout


def test_cli_list_solutions_error(mock_algorepo_class):
    mock_instance = mock_algorepo_class.return_value
    mock_instance.get_info.side_effect = SolutionsListError(path="/tmp/Solutions")

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 1
    assert "Error:" in result.stdout
    assert "Solutions directory not found" in result.stdout
