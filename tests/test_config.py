import pytest

from algorepo.config import Config, get_config_dir
from algorepo.exceptions import ConfigurationError


def test_config_defaults():
    config = Config()
    assert config.language_priority == ["Python3"]


def test_config_from_yaml(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("general:\n  language_priority:\n    - Java\n    - Python3\n")
    config = Config.from_yaml(config_file)
    assert config.language_priority == ["Java", "Python3"]


def test_config_missing_file_creates_template(tmp_path):
    target_path = tmp_path / "nonexistent.yaml"
    config = Config.from_yaml(target_path)
    assert isinstance(config, Config)
    assert target_path.exists()
    assert "solutions_dir: ~/Solutions" in target_path.read_text()


def test_get_config_dir_win32(mocker):
    mocker.patch("sys.platform", "win32")
    mocker.patch.dict("os.environ", {"APPDATA": "C:\\AppData"})
    path = get_config_dir()
    assert "AppData" in str(path)


def test_get_config_dir_unix(mocker):
    mocker.patch("sys.platform", "linux")
    path = get_config_dir()
    assert ".config/algorepo" in str(path)


def test_config_from_yaml_write_error(mocker, tmp_path):
    target_path = tmp_path / "nonexistent.yaml"
    mocker.patch("pathlib.Path.mkdir", side_effect=PermissionError)
    config = Config.from_yaml(target_path)
    # Should fallback to default config without raising Exception
    assert isinstance(config, Config)
    assert not target_path.exists()


def test_config_from_yaml_permission_error(mocker, tmp_path):
    target_path = tmp_path / "config.yaml"
    target_path.touch()
    mocker.patch("builtins.open", side_effect=PermissionError)
    with pytest.raises(ConfigurationError) as exc:
        Config.from_yaml(target_path)
    assert "cannot read config file" in str(exc.value)


def test_config_from_yaml_invalid_yaml(tmp_path):
    target_path = tmp_path / "config.yaml"
    target_path.write_text("general: [invalid yaml: {")
    with pytest.raises(ConfigurationError) as exc:
        Config.from_yaml(target_path)
    assert "Invalid config format" in str(exc.value)


def test_config_from_yaml_validation_error(tmp_path):
    target_path = tmp_path / "config.yaml"
    # Provide wrong type for language_priority (string instead of list)
    target_path.write_text("general:\n  language_priority: wrong_type\n")
    with pytest.raises(ConfigurationError) as exc:
        Config.from_yaml(target_path)
    assert "Invalid config format" in str(exc.value)
