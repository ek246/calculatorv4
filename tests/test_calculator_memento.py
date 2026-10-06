import pytest
from app.calculator_memento import CalculatorMemento
from decimal import Decimal
from app.calculation import Calculation
def test_to_dict():
    calc = Calculation(operation="multiplication", operand1=2, operand2=3)

    momento = CalculatorMemento(history=[calc])
    result = momento.to_dict()
    assert result["history"] == [calc.to_dict()]
    assert "timestamp" in result
    assert isinstance(result["timestamp"], str)
    assert result["timestamp"] == momento.timestamp.isoformat()
def test_from_dict():
    calc = Calculation(operation="addition", operand1=5, operand2=7)
    momento = CalculatorMemento(history=[calc])
    data = momento.to_dict()
    new_momento = CalculatorMemento.from_dict(data)
    assert new_momento.history[0].operation == "addition"
    assert new_momento.history[0].operand1 == 5
    assert new_momento.history[0].operand2 == 7
    assert new_momento.timestamp == momento.timestamp
