import pytest
import os
from decimal import Decimal
from pathlib import Path
from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError

# Set up temporary environment variables for testing
os.environ['CALCULATOR_MAX_HISTORY_SIZE'] = '500'
os.environ['CALCULATOR_AUTO_SAVE'] = 'false'
os.environ['CALCULATOR_PRECISION'] = '8'
os.environ['CALCULATOR_MAX_INPUT_VALUE'] = '1000'
os.environ['CALCULATOR_DEFAULT_ENCODING'] = 'utf-16'
os.environ['CALCULATOR_LOG_DIR'] = './test_logs'


# Helper function to clear specific environment variables
def clear_env_vars(*args):
    for var in args:
        os.environ.pop(var, None)

def test_default_configuration(monkeypatch):
    monkeypatch.setenv('CALCULATOR_LOG_DIR', './test_logs')
    monkeypatch.setenv('CALCULATOR_HISTORY_DIR', './test_history')
    monkeypatch.setenv('CALCULATOR_MAX_HISTORY_SIZE', '500')
    monkeypatch.setenv('CALCULATOR_AUTO_SAVE', 'false')
    monkeypatch.setenv('CALCULATOR_PRECISION', '8')
    monkeypatch.setenv('CALCULATOR_MAX_INPUT_VALUE', '1000')
    monkeypatch.setenv('CALCULATOR_DEFAULT_ENCODING', 'utf-16')
    config = CalculatorConfig()
    

def test_custom_configuration():
    config = CalculatorConfig(
        max_history_size=300,
        auto_save=True,
        precision=5,
        max_input_value=Decimal("500"),
        default_encoding="ascii"
    )
    assert config.max_history_size == 300
    assert config.auto_save is True
    assert config.precision == 5
    assert config.max_input_value == Decimal("500")
    assert config.default_encoding == "ascii"

def test_directory_properties():
    clear_env_vars('CALCULATOR_LOG_DIR', 'CALCULATOR_HISTORY_DIR')
    config = CalculatorConfig(base_dir=Path('/custom_base_dir'))
    assert config.log_dir == Path('/custom_base_dir/logs').resolve()
    assert config.history_dir == Path('/custom_base_dir/history').resolve()

def test_file_properties():
    clear_env_vars('CALCULATOR_HISTORY_FILE', 'CALCULATOR_LOG_FILE')
    config = CalculatorConfig(base_dir=Path('/custom_base_dir'))
    assert config.history_file == Path('/custom_base_dir/history/history.csv').resolve()
    assert config.log_file == Path('/custom_base_dir/logs/app.log').resolve()

def test_invalid_max_history_size():
    with pytest.raises(ConfigurationError, match="max_history_size can't be 0 or negative"):
        config = CalculatorConfig(max_history_size=-1)
        config.validate()

def test_invalid_precision():
    with pytest.raises(ConfigurationError, match="precision can't be 0 or negative"):
        config = CalculatorConfig(precision=-1)
        config.validate()

def test_invalid_max_input_value():
    with pytest.raises(ConfigurationError, match="max_input_value can't be 0 or negative"):
        config = CalculatorConfig(max_input_value=Decimal("-1"))
        config.validate()

def test_auto_save_env_var_true():
    os.environ['CALCULATOR_AUTO_SAVE'] = 'true'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is True

def test_auto_save_env_var_one():
    os.environ['CALCULATOR_AUTO_SAVE'] = '1'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is True

def test_auto_save_env_var_false():
    os.environ['CALCULATOR_AUTO_SAVE'] = 'false'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is False

def test_auto_save_env_var_zero():
    os.environ['CALCULATOR_AUTO_SAVE'] = '0'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is False

def test_environment_overrides():
    config = CalculatorConfig()
    assert config.max_history_size == 500
    assert config.auto_save is False
    assert config.precision == 8
    assert config.max_input_value == Decimal("1000")
    assert config.default_encoding == 'utf-16'

def test_default_fallbacks():
    # Clear all related environment variables and test default values
    clear_env_vars(
        'CALCULATOR_MAX_HISTORY_SIZE', 'CALCULATOR_AUTO_SAVE', 'CALCULATOR_PRECISION',
        'CALCULATOR_MAX_INPUT_VALUE', 'CALCULATOR_DEFAULT_ENCODING'
    )
    config = CalculatorConfig()
    assert config.max_history_size == 100
    assert config.auto_save is True
    assert config.precision == 2
    assert config.max_input_value == Decimal("1e6")
    assert config.default_encoding == 'utf-8'

def test_get_project_root():
    # Test that get_project_root() points to the correct path
    from app.calculator_config import get_project_root
    assert (get_project_root() / "app").exists()  # Adjust the path check as needed based on your file structure

def test_log_dir_property():
    # Clear environment to test base_dir path creation for log_dir
    clear_env_vars('CALCULATOR_LOG_DIR')
    config = CalculatorConfig(base_dir=Path('/new_base_dir'))
    assert config.log_dir == Path('/new_base_dir/logs').resolve()

def test_history_dir_property():
    # Clear environment to test base_dir path creation for history_dir
    clear_env_vars('CALCULATOR_HISTORY_DIR')
    config = CalculatorConfig(base_dir=Path('/new_base_dir'))
    assert config.history_dir == Path('/new_base_dir/history').resolve()

def test_log_file_property():
    # Clear environment to test base_dir path creation for log_file
    clear_env_vars('CALCULATOR_LOG_FILE')
    config = CalculatorConfig(base_dir=Path('/new_base_dir'))
    assert config.log_file == Path('/new_base_dir/logs/app.log').resolve()

def test_history_file_property():
    # Clear environment to test base_dir path creation for history_file
    clear_env_vars('CALCULATOR_HISTORY_FILE')
    config = CalculatorConfig(base_dir=Path('/new_base_dir'))
    assert config.history_file == Path('/new_base_dir/history/history.csv').resolve()
def test_base_dir_invalid(monkeypatch):
    monkeypatch.setenv('CALCULATOR_BASE_DIR', '/wrong/path' \
    '')

    config = CalculatorConfig()
    with pytest.raises(ConfigurationError, match="does not exist"):
        config.validate()