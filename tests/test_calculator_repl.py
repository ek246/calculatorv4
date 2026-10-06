from pathlib import Path
from app.calculator_repl import calculator_repl
from app.calculator import Calculator
from tests.test_calculator import test_save_history
from app.exceptions import OperationError, ValidationError
def test_calculator_repl_help(monkeypatch, capsys):
    inputs = iter(["help", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "\n Things you can do:" in captured.out
    assert "Available operations: addition, subtraction, multiplication, division, power, root" in captured.out
    assert "history - view calculation history" in captured.out
    assert "clear - clear calculation history" in captured.out
    assert "load - load calculation history from file" in captured.out
    assert "stop - exit the calculator" in captured.out
    assert "undo - undo the last operation from file" in captured.out
    assert "redo - redo the last undone operation from file" in captured.out
    assert "save - save calculation history to file" in captured.out
def test_history_lost(monkeypatch, capsys):
    inputs = iter(["stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    def bad_history():
        raise Exception("History lost")
    monkeypatch.setattr("app.calculator.Calculator.save_history", bad_history)
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "History lost" in captured.out
def test_save_blank_history(monkeypatch, capsys):
    history_file = Path("history/history.csv")
    history_file.parent.mkdir(parents=True, exist_ok=True)
    if history_file.exists():
        history_file.unlink()
    inputs = iter(["history", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "No history available." in captured.out
def test_history(monkeypatch, capsys):
    inputs = iter(["add", "2", "3", "history", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Result: 5" in captured.out
    assert "addition(2, 3) = 5" in captured.out
def test_clear_history(monkeypatch, capsys):
    inputs = iter(["clear", "history", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Calculation history cleared" in captured.out
    assert "No history available." in captured.out
def test_clear_history_error(monkeypatch, capsys):
    def raise_error():
        raise Exception("Error clearing history")
    monkeypatch.setattr("app.calculator.Calculator.clear_history", raise_error)
    inputs = iter(["clear", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Error clearing history" in captured.out
def test_load_history(monkeypatch, capsys):
    monkeypatch.setattr("app.calculator.Calculator.load_history", lambda self: None)
    inputs = iter(["load", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Calculation history loaded" in captured.out
def test_load_history_error(monkeypatch, capsys):
    def raise_error(self):
        raise Exception("Error loading history")
    monkeypatch.setattr("app.calculator.Calculator.load_history", raise_error)
    inputs = iter(["load", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Error loading history" in captured.out
def test_undo_unnecessary(monkeypatch, capsys):
    inputs = iter(["undo", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "No actions to undo." in captured.out
def test_undo_success(monkeypatch, capsys):
    inputs = iter(["add", "2", "3", "undo", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Last operation undone" in captured.out
def test_undo_failure(monkeypatch, capsys):
    def raise_error(self):
        raise Exception("Error undoing operation")
    monkeypatch.setattr("app.calculator.Calculator.undo", raise_error)
    inputs = iter(["undo", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Error undoing operation" in captured.out

def test_redo_unnecessary(monkeypatch, capsys):
    inputs = iter(["redo", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "No actions to redo." in captured.out

def test_redo_success(monkeypatch, capsys):
    inputs = iter(["add", "2", "3", "undo", "redo", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Last undone operation redone" in captured.out

def test_redo_failure(monkeypatch, capsys):
    def raise_error(self):
        raise Exception("Error redoing operation")
    monkeypatch.setattr("app.calculator.Calculator.redo", raise_error)
    inputs = iter(["redo", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Error redoing operation" in captured.out

def test_save_history(monkeypatch, capsys):
    monkeypatch.setattr("app.calculator.Calculator.save_history", lambda self: None)
    inputs = iter(["save", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Calculation history saved" in captured.out
def test_save_history_failure(monkeypatch, capsys):
    def raise_error(self):
        raise Exception("Error saving history")
    monkeypatch.setattr("app.calculator.Calculator.save_history", raise_error)
    inputs = iter(["save", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Error saving history" in captured.out
def test_cancel_operation(monkeypatch, capsys):
    inputs = iter(["add", "c", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Operation cancelled" in captured.out
def test_cancel_operation_second_operand(monkeypatch, capsys):
    inputs = iter(["add", "2", "c", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Operation cancelled" in captured.out
def test_operation_error(monkeypatch, capsys):
    inputs = iter(["add", "2", "3", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    def raise_error(self, *args, **kwargs):
        raise OperationError("Operation failed")
    monkeypatch.setattr("app.calculator.Calculator.perform_operation", raise_error)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Operation failed" in captured.out
def test_keyboard_interrupt(monkeypatch, capsys):
    inputs = iter(["add", "2", "3", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    def raise_keyboard_interrupt(self, *args, **kwargs):
        raise KeyboardInterrupt()
    monkeypatch.setattr("app.calculator.Calculator.perform_operation", raise_keyboard_interrupt)
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Calculator stopped" in captured.out
def test_EOF_error(monkeypatch, capsys):
    inputs = iter(["add", "2", "3"])
    def mock_input(_):
        raise EOFError()

    monkeypatch.setattr("builtins.input", mock_input)
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "No more input detected. Stopping calculator" in captured.out
def test_unexpected_exception(monkeypatch, capsys):
    inputs = iter(["add", "2", "3", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    def raise_unexpected_exception(self, *args, **kwargs):
        raise Exception("Unexpected error")
    monkeypatch.setattr("app.calculator.Calculator.perform_operation", raise_unexpected_exception)
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Unexpected error" in captured.out
def test_input_unknown(monkeypatch, capsys):
    inputs = iter(["unknown", "stop"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = calculator_repl()
    captured = capsys.readouterr()
    assert "Calculator has started. Type 'stop' to quit." in captured.out
