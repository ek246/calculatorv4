import datetime
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
        logging_info_mock.assert_any_call("Initialization complete")

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
    operation = OperationFactory.get_operation("subtraction")
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

def test_perform_operation_addition(calculator):
    operation = OperationFactory.get_operation("addition")
    calculator.set_operation(operation)
    result = calculator.perform_operation(5, 3)
    assert result == 8

def test_perform_operation_validation_error(calculator):
        calculator.set_operation(OperationFactory.get_operation("division"))
        with pytest.raises(ValidationError):
            calculator.perform_operation(5, "invalid")

def test_perform_operation_operation_error(calculator):
        with pytest.raises(OperationError, match = "You did not set an operation"):
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
     assert calculator.history == [(operation, (5, 3), 8)]

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
        'result': ['1'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    try:
         calculator.load_history()
         assert len(calculator.history) == 1
         assert calculator.history[0].operation == "Subtraction"
         assert calculator.history[0].operand1 == 3
         assert calculator.history[0].operand2 == 2
         assert calculator.history[0].result == 1
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
    mock_print.assert_any_call("\nThings you can do:")

@patch('builtins.input', side_effect=['add', '2', '3', 'stop'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")
    