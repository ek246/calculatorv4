import datetime
import logging
import logging
from pathlib import Path
import pandas as pd
import pytest 
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir = temp_path)
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:

         mock_log_dir.return_value = temp_path / "logs"
         mock_log_file.return_value = temp_path / "logs" / "calculator.log"
         mock_history_dir.return_value = temp_path / "history"
         mock_history_file.return_value = temp_path / "history" / "history.csv"
         yield Calculator(config=config)
def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')

        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Initialization complete.")

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

def test_set_operation(calculator):
    operation = OperationFactory.create_operation("subtraction")
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation("addition")
    calculator.set_operation(operation)
    result = calculator.perform_operation(5, 3)
    assert result == 8

def test_perform_operation_validation_error(calculator):
        calculator.set_operation(OperationFactory.create_operation("division"))
        with pytest.raises(ValidationError):
            calculator.perform_operation(5, "invalid")

def test_perform_operation_operation_error(calculator):
        with pytest.raises(OperationError, match = "No operation is set"):
             calculator.perform_operation(3, 3)

def test_undo(calculator):
     operation = OperationFactory.create_operation("addition")
     calculator.set_operation(operation)
     result = calculator.perform_operation(5, 3)
     assert result == 8
     calculator.undo()
     assert calculator.history == []

def test_redo(calculator):
     operation = OperationFactory.create_operation("addition")
     calculator.set_operation(operation)
     result = calculator.perform_operation(5, 3)
     assert result == 8
     calculator.undo()
     assert calculator.history == []
     calculator.redo()
     assert len(calculator.history) == 1
     assert calculator.history[0].operation == "addition"
     assert calculator.history[0].operand1 == 5
     assert calculator.history[0].operand2 == 3
     assert calculator.history[0].outcome == 8
@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
     operation = OperationFactory.create_operation("addition")
     calculator.set_operation(operation)
     calculator.perform_operation(4, 5)
     calculator.save_history()
     mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    mock_read_csv.return_value = pd.DataFrame({
         'operation': ['Subtraction'],
        'operand1': ['3'],
        'operand2': ['2'],
        'outcome': ['1'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    try:
         calculator.load_history()
         assert len(calculator.history) == 1
         assert calculator.history[0].operation == "Subtraction"
         assert calculator.history[0].operand1 == 3
         assert calculator.history[0].operand2 == 2
         assert calculator.history[0].outcome == 1
    except OperationError as e:
         pytest.fail(f"Loading history failed: {e}")

    def test_clear_history(calculator):
         operation = OperationFactory.create_operation("addition")
         calculator.set_operation(operation)
         calculator.perform_operation(4, 5)
         calculator.clear_history()
         assert calculator.history == []
         assert calculator.undo_stack == []
         assert calculator.redo_stack == []

@patch('builtins.input', side_effect=['stop'])
@patch('builtins.print')
def test_calculator_repl_stop(mock_print, mock_input):
     with patch('app.calculator.Calculator.save_history') as mock_save_history:
          calculator_repl()
          mock_save_history.assert_called_once()
          mock_print.assert_any_call("Stopping the calculator.")

@patch('builtins.input', side_effect=['help', 'stop'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
     calculator_repl()
     assert "\n Things you can do:" in [call.args[0] for call in mock_print.call_args_list]
@patch('builtins.input', side_effect=['add', '2', '3', 'stop'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")
def test_logging_initialization_failure():
     with patch('app.calculator.logging.basicConfig') as mock_basicConfig, \
          patch('app.calculator.logging.error') as mock_logging_error:
         mock_basicConfig.side_effect = Exception("Initialization failed")
         Calculator(CalculatorConfig())
         mock_logging_error.assert_called_once()
def test_cannot_find_observer():
     with patch('app.calculator.logging.warning') as mock_logging_warning:
        calculator = Calculator(CalculatorConfig())
        class TestObserver:
            pass
        lost_observer = TestObserver()
        calculator.remove_observer(lost_observer)

        mock_logging_warning.assert_called_once_with (
        "Observer not found: TestObserver"
    )

def test_self_history_removal(calculator):
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path, max_history_size=1)
        calculator = Calculator(config)

        operation = OperationFactory.create_operation("addition")
        calculator.set_operation(operation)
        calculator.perform_operation(4, 5)
        calculator.perform_operation(6, 7)
        assert len(calculator.history) == 1
        assert calculator.history[0].operand1 == 6
        assert calculator.history[0].operand2 == 7
def test_failed_operation(calculator):
    operation = OperationFactory.create_operation("division")
    calculator.set_operation(operation)
    with pytest.raises(OperationError):
        calculator.perform_operation(4, 0)

def test_save_history_error(calculator):
    calculator.clear_history()
    with patch(
        "app.calculator.pd.DataFrame.to_csv", side_effect=Exception("Save failed")
    ):
        with pytest.raises(OperationError, match="Could not save history: Save failed"):
            calculator.save_history()
def test_load_history_error(calculator):
    calculator.config.history_file.parent.mkdir(parents=True, exist_ok=True)
    calculator.config.history_file.touch()
    with patch(
        "app.calculator.pd.read_csv", side_effect=Exception("Load failed")
    ):
        with pytest.raises(OperationError, match="Could not load history: Load failed"):
            calculator.load_history()
def test_load_history_dataframe(calculator):
    calculator.clear_history()
    operation = OperationFactory.create_operation("addition")
    calculator.set_operation(operation)
    calculator.perform_operation(4, 5)
    df = calculator.load_history_dataframe()
    assert not df.empty
    assert list(df.columns) == ["operation", "operand1", "operand2", "outcome", "timestamp"]
    assert df.iloc[0]["operation"] == "addition"
    assert df.iloc[0]["operand1"] == "4"
    assert df.iloc[0]["operand2"] == "5"
    assert df.iloc[0]["outcome"] == "9"
    assert df.iloc[0]["timestamp"] is not None
def test_load_history_file_does_not_exist(calculator):
    if calculator.config.history_file.exists():
        calculator.config.history_file.unlink()
    calculator.load_history()
    assert calculator.history == []
    
def test_load_history_dataframe_empty(calculator):
    calculator.clear_history()
    df = calculator.load_history_dataframe()
    assert len(df) == 0


          