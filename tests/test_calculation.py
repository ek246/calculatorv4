from sys import exc_info

import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError, ValidationError
import logging

def test_addition():
    calc = Calculation(operation='addition', operand1=Decimal('2'), operand2=Decimal('3'))
    assert calc.outcome == Decimal('5')

def test_subtraction():
    calc = Calculation(operation='subtraction', operand1=Decimal('5'), operand2=Decimal('3'))
    assert calc.outcome == Decimal('2')

def test_multiplication():
    calc = Calculation(operation='multiplication', operand1=Decimal('2'), operand2=Decimal('3'))
    assert calc.outcome == Decimal('6')

def test_division():
    calc = Calculation(operation='division', operand1=Decimal('6'), operand2=Decimal('3'))
    assert calc.outcome == Decimal('2')

def test_division_by_zero():
    with pytest.raises(OperationError, match="You cannot divide by zero"):
        Calculation(operation='division', operand1=Decimal('6'), operand2=Decimal('0'))

def test_power():
    calc = Calculation(operation='power', operand1=Decimal('2'), operand2=Decimal('3'))
    assert calc.outcome == Decimal('8')

def test_negative_power():
    with pytest.raises(OperationError, match="This calculator does not support negative exponents"):
        Calculation(operation='power', operand1=Decimal('2'), operand2=Decimal('-3'))

def test_root():
    calc = Calculation(operation = 'root', operand1 = Decimal('16'), operand2 = Decimal('2'))
    assert calc.outcome == Decimal('4')

def test_negative_root():
    with pytest.raises(OperationError, match="Cannot calculate a negative number's root"):
        Calculation(operation='root', operand1=Decimal('-16'), operand2=Decimal('2'))
def test_zero_root():
    with pytest.raises(OperationError, match="Root cannot be zero"):
        Calculation(operation='root', operand1=Decimal('16'), operand2=Decimal('0'))


def test_invalid_operation():
    with pytest.raises(OperationError, match="This operation is not supported"):
        Calculation(operation='invalid', operand1=Decimal('2'), operand2=Decimal('3'))

def test_to_dict():

   calc = Calculation(operation='addition', operand1=Decimal('2'), operand2=Decimal('3'))

   result_dict = calc.to_dict()

   assert result_dict == {

       "operation": "addition",

        "operand1": "2",

        "operand2": "3",

        "outcome": "5",

        "timeOfCalc": calc.timeOfCalc.isoformat()
    }

def test_from_dict():
    data = {
        'operation': 'subtraction',
        'operand1': Decimal('5'),
        'operand2': Decimal('3'),
        'outcome': Decimal('2'),
        "timeOfCalc": datetime.now().isoformat()
    }
    calc = Calculation.from_dict(data)
    assert calc.operation == 'subtraction'
    assert calc.operand1 == Decimal('5')
    assert calc.operand2 == Decimal('3')
    assert calc.outcome == Decimal('2')
def test_invalid_from_dict():
    data = {
        'operation': 'invalid',
        'operand1': Decimal('2'),
        'operand2': Decimal('3'),
        'outcome': Decimal('5'),
        "timeOfCalc": datetime.now().isoformat()
    }
    with pytest.raises(OperationError, match="This operation is not supported"):
        Calculation.from_dict(data)
def test_format_results():
    calc = Calculation(operation = "division", operand1=Decimal('1'), operand2=Decimal('3'))
    assert calc.format_result(precision = 2) == '0.33'
    assert calc.format_result(precision = 5) == '0.33333'
def test_equality():
    calc1 = Calculation(operation='addition', operand1=Decimal('2'), operand2=Decimal('3'))
    calc2 = Calculation(operation='addition', operand1=Decimal('2'), operand2=Decimal('3'))
    calc3 = Calculation(operation='subtraction', operand1=Decimal('5'), operand2=Decimal('3'))
    calc1.timeOfCalc = calc2.timeOfCalc
    assert calc1 == calc2
    assert calc1 != calc3
def test_logging_from_dict_mismatch(caplog):
    data = {
        'operation': 'addition',
        'operand1': Decimal('2'),
        'operand2': Decimal('3'),
        'outcome': Decimal('11'),
        'timeOfCalc': datetime.now().isoformat()
    }
    with caplog.at_level(logging.WARNING):
        calc= Calculation.from_dict(data)

    assert "This is a mismatch: calculated 5, saved 11" in caplog.text

def test_error_creating_calculation_from_dict():
    data = {
        'operation': 'addition',
        'operand1': 'invalid',
        'operand2': Decimal('3'),
        'outcome': Decimal('5'),
        "timeOfCalc": datetime.now().isoformat()
    }
    with pytest.raises(OperationError, match="Error creating Calculation from dict:"):
        Calculation.from_dict(data)
def test__str__():
    calc = Calculation(operation='addition', operand1=Decimal('2'), operand2=Decimal('3'))
    expected_str = f"Calculation(operation=addition, operand1=2, operand2=3, outcome=5, timeOfCalc={calc.timeOfCalc})"
    assert str(calc) == expected_str
def test__repr__():
    calc = Calculation(operation='addition', operand1=Decimal('2'), operand2=Decimal('3'))
    expected_repr = f"Calculation(operation=addition, operand1=2, operand2=3, outcome=5, timeOfCalc={calc.timeOfCalc})"
    assert repr(calc) == expected_repr
def test__eq__not_implemented():
    calc = Calculation(operation='addition', operand1=Decimal('2'), operand2=Decimal('3'))
    not_calc = "I am not a Calculation instance"
    assert calc.__eq__(not_calc) is NotImplemented
def test_format_result_error():
    calc = Calculation(operation='addition', operand1=Decimal('1'), operand2=Decimal('0'))
    calc.outcome = Decimal('Infinity')
    result = calc.format_result(precision=2)
    assert result == 'Infinity' 
def test_operation_performance_error():
    with pytest.raises(OperationError, match="Error performing subtraction:"):
        Calculation(operation='subtraction', operand1=Decimal('sNAN'), operand2=Decimal('2'))


