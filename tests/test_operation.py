
import pytest
from typing import Union
from app.operations import Operations
Digit = Union[float, int]

@pytest.mark.parametrize(
    "a, b, expected",
    [(1,2,3),
     (0,0,0),
     (1,-2,-1),
     (-1,-1,-2),
     (1.5, 2.5, 4.0),
     (-1.5, -2.5, -4.0),
    (-1.5, 2.5, 1.0),
    ],
    ids = [
        "add positive integers",
        "add zeros",
        "add positive and negative integers",
        "add negative integers",
        "add positive floats",
        "add negative floats",
        "add negative and positive floats",
    ]
)
def test_addition(a: Digit, b: Digit, expected: Digit) -> None:
        """Test addition operation."""
        result = Operations.addition(a, b)
        assert result == expected, f"{a} + {b} should be {expected}, not {result}"


@pytest.mark.parametrize(
    "a, b, expected",
    [(1,2,-1),
     (0,0,0),
     (1,-2,3),
     (-1,-1,0),
     (1.5, 2.5, -1.0),
     (-1.5, -2.5, 1.0),
     (-1.5, 2.5, -4.0),
    ],
    ids = [
        "subtract positive integers",
        "subtract zeros",
        "subtract positive and negative integers",
        "subtract negative integers",
        "subtract positive floats",
        "subtract negative floats",
        "subtract negative and positive floats",
    ]
)
def test_subtraction(a: Digit, b: Digit, expected: Digit) -> None:
        """Test subtraction operation."""
        result = Operations.subtraction(a, b)
        assert result == expected, f"{a} - {b} should be {expected}, not {result}"

@pytest.mark.parametrize(
    "a, b, expected",
    [(1,1,1),
     (-2, -1, 2),
     (1,-1,-1),
     (0,-1,0),
     (1.5, 1.5, 1),
     (-1.5, 2.5, -0.6),
     (-1.5, -1.5,1)],
    ids = [
        "divide positive integers",
        "divide negative integers",
        "divide positive and negative integers",
        "divide negative integer and zero",
        "divide positive floats",
        "divide negative and positive floats",
        "divide negative floats",
    ]
)
def test_division(a: Digit, b: Digit, expected: Digit) -> None:
        """Test division operation."""
        result = Operations.division(a, b)
        assert result == expected, f"{a} / {b} should be {expected}, not {result}"
@pytest.mark.parametrize(
    "a, b",
    [(1,0),
    (-2, 0),  
    (0,0),
    (-1.5, 0)],
    ids = [
        "divide positive integer by zero",
        "divide negative integer by zero",
        "divide zero by zero",
        "divide negative float by zero",
    ]
)
def test_division_by_zero(a: Digit, b: Digit) -> None:
        """Test division by zero operation."""
        with pytest.raises(ZeroDivisionError) as excinfo:
            Operations.division(a, b)
        assert str(excinfo.value) == "You cannot divide by zero."
@pytest.mark.parametrize(
    "a, b, expected",
    [(1,2,2),
    (0,0,0),
    (1,-2,-2),
    (-1,-1,1),
    (1.5, 2.5, 3.75),
    (-1.5, -2.5, 3.75),
    (-1.5, 2.5, -3.75)],
    ids = [
        "multiply positive integers",
        "multiply zeros",
        "multiply positive and negative integers",
        "multiply negative integers",
        "multiply positive floats",
        "multiply negative floats",
        "multiply negative and positive floats",
    ]
)
def test_multiplication(a: Digit, b: Digit, expected: Digit) -> None:
        """Test multiplication operation."""
        result = Operations.multiplication(a, b)
        assert result == expected, f"{a} * {b} should be {expected}, not {result}"
