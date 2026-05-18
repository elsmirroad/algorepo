from algorepo.config import Config


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
